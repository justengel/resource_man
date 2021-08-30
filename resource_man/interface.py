import copy
import contextlib
from .importlib_interface import Traversable, contents, is_resource, read_binary, read_text, files, as_file


__all__ = [
    'ResourceNotAvailable', 'Resource', 'ResourceManager', 'get_global_manager', 'set_global_manager', 'temp_manager',
    'register', 'has_resource', 'get_resources', 'get_resource', 'get_binary', 'get_text']


class MISSING:
    pass


class ResourceNotAvailable(Exception):
    pass


class Resource:
    def __init__(self, package, name, identifier=None, **kwargs):
        """Initialize the resource object.

        Args:
            package (str): Package or module name where the resource can be found (EX: "mylib.mysubpkg")
            name (str): Name of the resource (EX: "myimg.png").
            identifier (str)[None]: Shortcut identifier for the resource. This is the same identifier used in register.
            **kwargs (dict): Dictionary of keyword arguments to set as resource attributes.
        """
        self._identifier = identifier
        self.package = package
        self.name = name

        # Set all keyword arguments as attributes
        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except (AttributeError, TypeError, ValueError):
                pass

    def get_package_path(self):
        """Return the package path."""
        return '/'.join((self.package.replace('.', '/'), self.name))

    @property
    def identifier(self):
        """Return the registered resource identifier."""
        if self._identifier is None:
            return self.get_package_path()
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    def is_resource(self):
        return is_resource(self.package, self.name)

    def files(self):
        return files(self.package).joinpath(self.name)

    @contextlib.contextmanager
    def as_file(self):
        with as_file(self.files()) as filename:
            yield filename

    def contents(self):
        return contents(self.package)

    def read_bytes(self):
        error = None
        try:
            return read_binary(self.package, self.name)
        except Exception as err:
            error = err
        raise ResourceNotAvailable(str(error))

    read_binary = read_bytes

    def read_text(self, encoding='utf-8', errors='strict'):
        error = None
        try:
            return read_text(self.package, self.name, encoding, errors)
        except Exception as err:
            error = err
        raise ResourceNotAvailable(str(error))

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.identifier or other == self.get_package_path()
        return super().__eq__(other)


class ResourceManager(list):
    def __getitem__(self, item):
        for rsc in self:
            if rsc == item:
                return rsc

        raise ResourceNotAvailable("The requested resouce was not found!")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            super().__setitem__(key, value)
            return

        # Find the resource and replace the identifier
        for rsc in self:
            if rsc == value:
                rsc.identifier = key
                return

        # If not found add the resource to the list.
        self.append(value)

    def register(self, identifier, package, name, **kwargs):
        """Register a resource to an identifier."""
        rsc = Resource(package, name, identifier=identifier, **kwargs)
        self.append(rsc)
        return rsc

    def has_resource(self, identifier):
        """Return if the registered resource exists."""
        return identifier in self

    def get_resources(self):
        """Return a list of registered resources."""
        return copy.copy(self)

    def get_resource(self, identifier, fallback=None, default=MISSING):
        """Return the Resource object from the given identifier or default.

        Args:
            identifier (str): Identifier that has a registered resource
            fallback (str)[None]: Fallback identifier if the given identifier was not registered.
            default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
        """
        # Try finding the identifier
        try:
            return self[identifier]
        except KeyError:
            pass

        # Try fallback
        try:
            if isinstance(fallback, Resource):
                return fallback
            return self[fallback]
        except KeyError:
            pass

        # Check default
        if default is MISSING:
            raise ResourceNotAvailable('Resource "{}" not found'.format(identifier))
        return default

    def get_binary(self, identifier, fallback=None, default=MISSING):
        """Return the binary data for the Resource object from the given identifier or default.

        Args:
            identifier (str): Identifier that has a registered resource
            fallback (str)[None]: Fallback identifier if the given identifier was not registered.
            default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
        """
        rsc = self.get_resource(identifier, fallback, default)
        if isinstance(rsc, Resource):
            return rsc.read_binary()
        return rsc

    def get_text(self, identifier, fallback=None, default=MISSING, encoding='utf-8', errors='strict'):
        """Return the text data for the Resource object from the given identifier or default.

        Args:
            identifier (str): Identifier that has a registered resource
            fallback (str)[None]: Fallback identifier if the given identifier was not registered.
            default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
            encoding (str)['utf-8']: Encoding to convert binary data to text.
            errors (str)['strict']: Error handling code when converting the binary data to text.
        """
        rsc = self.get_resource(identifier, fallback, default)
        if isinstance(rsc, Resource):
            return rsc.read_text(encoding=encoding, errors=errors)
        return rsc


RESOURCE_MANAGER = ResourceManager()


def get_global_manager():
    """Return the global ResourceManager."""
    global RESOURCE_MANAGER
    return RESOURCE_MANAGER


def set_global_manager(manager):
    """Set the global ResourceManager."""
    global RESOURCE_MANAGER
    RESOURCE_MANAGER = manager


@contextlib.contextmanager
def temp_manager(manager):
    """Temporarily change the global resource manager using this with context."""
    old = get_global_manager()
    set_global_manager(manager)
    try:
        yield
    finally:
        set_global_manager(old)


def register(identifier, package, name, **kwargs):
    """Register a resource to an identifier."""
    return get_global_manager().register(identifier, package, name, **kwargs)


def has_resource(identifier):
    """Return if the registered resource exists."""
    return get_global_manager().has_resource(identifier)


def get_resources():
    """Return a list of registered resources."""
    return get_global_manager().get_resources()


def get_resource(identifier, fallback=None, default=MISSING):
    """Return the Resource object from the given identifier or default.

    Args:
        identifier (str): Identifier that has a registered resource
        fallback (str)[None]: Fallback identifier if the given identifier was not registered.
        default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
    """
    return get_global_manager().get_resource(identifier, fallback=fallback, default=default)


def get_binary(identifier, fallback=None, default=MISSING):
    """Return the binary data for the Resource object from the given identifier or default.

    Args:
        identifier (str): Identifier that has a registered resource
        fallback (str)[None]: Fallback identifier if the given identifier was not registered.
        default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
    """
    return get_global_manager().get_binary(identifier, fallback=fallback, default=default)


def get_text(identifier, fallback=None, default=MISSING, encoding='utf-8', errors='strict'):
    """Return the text data for the Resource object from the given identifier or default.

    Args:
        identifier (str): Identifier that has a registered resource
        fallback (str)[None]: Fallback identifier if the given identifier was not registered.
        default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
        encoding (str)['utf-8']: Encoding to convert binary data to text.
        errors (str)['strict']: Error handling code when converting the binary data to text.
    """
    return get_global_manager().get_text(identifier, fallback=fallback, default=default,
                                         encoding=encoding, errors=errors)
