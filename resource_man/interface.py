import os
import sys
import copy
import atexit
import contextlib
from .importlib_interface import Traversable, contents, is_resource, read_binary, read_text, files, as_file

try:
    from dataclasses import MISSING
except (ImportError, Exception):
    MISSING = object()


__all__ = [
    'ResourceNotAvailable', 'Resource', 'ResourceManager', 'get_global_manager', 'set_global_manager', 'temp_manager',
    'clear', 'register', 'register_directory', 'unregister', 'has_resource', 'get_resources', 'get_resource',
    'get_binary', 'get_text',
    'MISSING'
    ]


class ResourceNotAvailable(Exception):
    pass


class Resource:
    def __init__(self, package, name, alias=MISSING, **kwargs):
        """Initialize the resource object.

        Args:
            package (str): Package or module name where the resource can be found (EX: "mylib.mysubpkg")
            name (str): Name of the resource (EX: "myimg.png").
            alias (str)[MISSING]: Shortcut alias name identifer for the resource.
                ... (Ellipsis) will be the name with the extension (EX: "myimg.png")
                None will be the name without the extension (EX: "myimg")
            **kwargs (dict): Dictionary of keyword arguments to set as resource attributes.
        """
        self.raw_alias = alias
        self.package = package
        self.name = name
        self._context = None
        self._context_obj = None

        # Set all keyword arguments as attributes
        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except (AttributeError, TypeError, ValueError):
                pass

    @property
    def package_path(self):
        """Return the package path."""
        return '/'.join((self.package.replace('.', '/'), self.name))

    @property
    def alias(self):
        """Return the alias name identifier."""
        if self.raw_alias is MISSING:
            return self.package_path
        elif self.raw_alias is ...:
            return self.name
        elif self.raw_alias is None:
            return os.path.splitext(self.name)[0]
        return self.raw_alias

    @alias.setter
    def alias(self, value):
        self.raw_alias = value

    # Backwards compatibility support
    identifier = alias

    def is_resource(self):
        return is_resource(self.package, self.name)

    def files(self):
        return files(self.package).joinpath(self.name)

    @contextlib.contextmanager
    def as_file(self):
        with as_file(self.files()) as file:
            yield file

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

    def _enter_context(self):
        """Use "as_file" to enter the with context block for the life of the application in order to get the filepath.
        """
        self._context = self.as_file()
        self._context_obj = self._context.__enter__()
        try:
            self._context_obj = self._context_obj.resolve()  # Get proper path capitalization
        except (AttributeError, Exception):
            pass
        atexit.register(self._exit_context)

    def _exit_context(self):
        """Exit the context object that was used with "as_file"."""
        try:
            self._context.__exit__()
        except (ResourceNotAvailable, OSError, TypeError, ValueError, Exception):
            pass
        finally:
            self._context_obj = None
            self._context = None

    def __str__(self):
        """Return the full string file path. I'm not sure if this will always work. "as_file" should be used."""
        try:
            if self._context_obj:
                return str(self._context_obj)

            # Use "as_file" to enter the context and return the filepath
            self._enter_context()
            if self._context_obj:
                return str(self._context_obj)

            # Use files to return the path. Should I even do this?
            filename = self.files()
            try:
                filename = filename.resolve()
            except (AttributeError, OSError, Exception):
                pass
            return str(filename)
        except (ResourceNotAvailable, OSError, TypeError, ValueError, Exception):
            pass

        # Return the simple package path from the working directory.
        pp = orig_pp = str(self.package_path)
        if not os.path.exists(pp):
            pp = os.path.join(getattr(sys, '_MEIPASS', sys.executable), pp)
            if not os.path.exists(pp):
                pp = orig_pp
        return pp

    def __fspath__(self):
        """Return the file path. This is not recommended. You should be using 'as_file' or 'read_text'."""
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.alias or other == self.package_path
        return super().__eq__(other)

    def __repr__(self):
        kwargs = {'cls': self.__class__.__name__, 'package': self.package, 'name': self.name, 'alias': self.alias}
        if self.raw_alias:
            return '{cls}(package={package}, name={name}, alias={alias})'.format(**kwargs)
        else:
            return '{cls}(package={package}, name={name})'.format(**kwargs)


class ResourceManager(list):

    RESOURCE_CLASS = Resource

    def __getitem__(self, item):
        if isinstance(item, int):
            return super().__getitem__(item)

        for rsc in reversed(self):
            if rsc == item:
                return rsc

        raise ResourceNotAvailable("The requested resouce was not found!")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            super().__setitem__(key, value)
            return
        elif isinstance(key, self.RESOURCE_CLASS):
            key = key.alias or key.package_path

        # Find the resource and replace the identifier
        for i in reversed(range(len(self))):
            rsc = self[i]
            if rsc.alias == key:
                super().__setitem__(i, value)
                return

        # If not found add the resource to the list.
        self.append(value)

    def register(self, package, name, alias=MISSING, **kwargs):
        """Register a resource. You can optionally have an alias name identifier.
        When using the alias the last resource registered with the same alias will be used.

        Args:
            package (str): Package name ('check_lib.check_sub')
            name (str): Name of the resource ('edit-cut.png')
            alias (str)[MISSING]: Shortcut alias name identifer for the resource.
                ... (Ellipsis) will be the name with the extension (EX: "myimg.png")
                None will be the name without the extension (EX: "myimg")
            **kwargs (dict): Dictionary of keyword arguments to set as attributes to the resource.
        """
        rsc = self.RESOURCE_CLASS(package, name, alias=alias, **kwargs)
        self.append(rsc)
        return rsc

    def register_directory(self, package, extensions=None, exclude=None, **kwargs):
        """Register all items in a directory.

        Note:
            This does not register the __init__.py module.

        Args:
            package (str): Package name ('check_lib.check_sub')
            extensions (list/str)[None]: List of extensions to register (".csv", ".txt", "" for "LICENSE" with no ext).
                If None register all.
            exclude (list/str)[None]: List of filenames to exclude.
            **kwargs (dict): Dictionary of keyword arguments to set as attributes to the resource.

        Returns:
            directory (list): List of Resource objects that were registered.
        """
        if isinstance(extensions, str):
            extensions = [extensions]
        if exclude is None:
            exclude = []
        elif isinstance(exclude, str):
            exclude = [exclude]

        directory = []
        for name in contents(package):
            name = str(name)
            ext = os.path.splitext(name)[-1]
            if (name not in exclude) and (extensions is None or ext in extensions):
                directory.append(self.register(package, name, **kwargs))

        return directory

    def unregister(self, rsc=None, name=None, alias=None):
        """Unregister a resource.

        Args:
            rsc (str/Resource)[None]: Resource to unregister or package name (with name argument) or alias.
            name (str)[None]: Required if package name given
            alias (str)[None]: Alias name identifier to find. This may also be given as first argument.

        Returns:
            rsc (Resource): Resource that was found

        Raises:
            error (ResourceNotAvailable): Resource was not found!
        """
        if isinstance(rsc, str) and isinstance(name, str):
            rsc = '/'.join((rsc.replace('.', '/'), name))
        elif isinstance(alias, str):
            rsc = alias

        for i in reversed(range(len(self))):
            resource = self[i]
            if resource == rsc:
                return self.pop(i)

        raise ResourceNotAvailable('Resource not found! If "package" given then the "name" argument is required.')

    def has_resource(self, rsc=None, name=None, alias=None):
        """Return if the registered resource exists (this can be the alias, resource, or package_path."""
        if isinstance(rsc, str) and isinstance(name, str):
            rsc = '/'.join((rsc.replace('.', '/'), name))
        elif isinstance(alias, str):
            rsc = alias

        return rsc in self

    def get_resources(self):
        """Return a list of registered resources.

        If multiple resources have the same alias the last one will be used.
        """
        return copy.copy(self)

    def get_resource(self, rsc, fallback=None, default=MISSING):
        """Return the found Resource object from the given resource, fallback, or default value.

        Args:
            rsc (str/Resource): Alias name identifier, package path, or Resource object that has a registered resource
            fallback (str)[None]: Fallback alias if the given alias was not registered.
            default (object)[MISSING]: Default value to return if the alias and fallback were not found.

        Returns:
            rsc (Resource): The found Resource object.
        """
        # Try finding the identifier
        try:
            return self[rsc]
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
            raise ResourceNotAvailable('Resource "{}" not found'.format(rsc))
        return default

    def get_binary(self, rsc, fallback=None, default=MISSING):
        """Return the binary data for the Resource object from the given identifier or default.

        Args:
            rsc (str/Resource): Alias name identifier, package path, or Resource object that has a registered resource
            fallback (str)[None]: Fallback alias if the given alias was not registered.
            default (object)[MISSING]: Default value to return if the alias and fallback were not found.

        Returns:
            data (bytes): Binary data that was read.
        """
        rsc = self.get_resource(rsc, fallback, default)
        if isinstance(rsc, Resource):
            return rsc.read_binary()
        return rsc

    def get_text(self, rsc, fallback=None, default=MISSING, encoding='utf-8', errors='strict'):
        """Return the text data for the Resource object from the given identifier or default.

        Args:
            rsc (str/Resource): Alias name identifier, package path, or Resource object that has a registered resource
            fallback (str)[None]: Fallback alias if the given alias was not registered.
            default (object)[MISSING]: Default value to return if the alias and fallback were not found.
            encoding (str)['utf-8']: Encoding to convert binary data to text.
            errors (str)['strict']: Error handling code when converting the binary data to text.

        Returns:
            text (str): Text data that was read.
        """
        rsc = self.get_resource(rsc, fallback, default)
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


def clear():
    """Clear out all of the resources that are registered."""
    get_global_manager().clear()


def register(package, name, alias=MISSING, **kwargs):
    """Register a resource. You can optionally have an alias name identifier.
    When using the alias the last resource registered with the same alias will be used.

    Args:
        package (str): Package name ('check_lib.check_sub')
        name (str): Name of the resource ('edit-cut.png')
        alias (str)[MISSING]: Shortcut alias name identifer for the resource.
            ... (Ellipsis) will be the name with the extension (EX: "myimg.png")
            None will be the name without the extension (EX: "myimg")
        **kwargs (dict): Dictionary of keyword arguments to set as attributes to the resource.
    """
    return get_global_manager().register(package, name, alias=alias, **kwargs)


def register_directory(package, extensions=None, exclude=None, **kwargs):
    """Register all items in a directory.

    Note:
        This does not register the __init__.py module.

    Args:
        package (str): Package name ('check_lib.check_sub')
        extensions (list/str)[None]: List of extensions to register (".csv", ".txt", "" for "LICENSE" with no ext).
            If None register all.
        exclude (list/str)[None]: List of filenames to exclude.
        **kwargs (dict): Dictionary of keyword arguments to set as attributes to the resource.

    Returns:
        directory (list): List of Resource objects that were registered.
    """
    return get_global_manager().register_directory(package, extensions=extensions, exclude=exclude, **kwargs)


def unregister(rsc=None, name=None, alias=None):
    """Unregister a resource.

    Args:
        rsc (str/Resource)[None]: Resource to unregister or package name (with name argument) or alias.
        name (str)[None]: Required if package name given
        alias (str)[None]: Alias name identifier to find. This may also be given as first argument.

    Returns:
        rsc (Resource): Resource that was found

    Raises:
        error (ResourceNotAvailable): Resource was not found!
    """
    return get_global_manager().unregister(rsc=rsc, name=name, alias=alias)


def has_resource(rsc=None, name=None, alias=None):
    """Return if the registered resource exists (this can be the alias, resource, or package_path."""
    return get_global_manager().has_resource(rsc=rsc, name=name, alias=alias)


def get_resources():
    """Return a list of registered resources.

    If multiple resources have the same alias the last one will be used.
    """
    return get_global_manager().get_resources()


def get_resource(rsc, fallback=None, default=MISSING):
    """Return the found Resource object from the given resource, fallback, or default value.

    Args:
        rsc (str/Resource): Alias name identifier, package path, or Resource object that has a registered resource
        fallback (str)[None]: Fallback alias if the given alias was not registered.
        default (object)[MISSING]: Default value to return if the alias and fallback were not found.

    Returns:
        rsc (Resource): The found Resource object.
    """
    return get_global_manager().get_resource(rsc, fallback=fallback, default=default)


def get_binary(rsc, fallback=None, default=MISSING):
    """Return the binary data for the Resource object from the given identifier or default.

    Args:
        rsc (str/Resource): Alias name identifier, package path, or Resource object that has a registered resource
        fallback (str)[None]: Fallback alias if the given alias was not registered.
        default (object)[MISSING]: Default value to return if the alias and fallback were not found.

    Returns:
        data (bytes): Binary data that was read.
    """
    return get_global_manager().get_binary(rsc, fallback=fallback, default=default)


def get_text(rsc, fallback=None, default=MISSING, encoding='utf-8', errors='strict'):
    """Return the text data for the Resource object from the given identifier or default.

    Args:
        rsc (str/Resource): Alias name identifier, package path, or Resource object that has a registered resource
        fallback (str)[None]: Fallback alias if the given alias was not registered.
        default (object)[MISSING]: Default value to return if the alias and fallback were not found.
        encoding (str)['utf-8']: Encoding to convert binary data to text.
        errors (str)['strict']: Error handling code when converting the binary data to text.

    Returns:
        text (str): Text data that was read.
    """
    return get_global_manager().get_text(rsc, fallback=fallback, default=default, encoding=encoding, errors=errors)
