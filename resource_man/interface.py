from .importlib_interface import Traversable, files, as_file, read_binary, read_text, contents, is_resource


__all__ = ['ResourceNotAvailable', 'Resource', 'register', 'has_resource', 'get_resources', 'get_resource',
           'get_binary', 'get_text']


class MISSING:
    pass


class ResourceNotAvailable(Exception):
    pass


class Resource:
    def __init__(self, package, name):
        self.package = package
        self.name = name

    def is_resource(self):
        return is_resource(self.package, self.name)

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


RESOURCES = {}


def register(identifier, package, name):
    """Register a resource to an identifier."""
    RESOURCES[identifier] = res = Resource(package, name)
    return res


def has_resource(identifier):
    """Return if the registered resource exists."""
    return identifier in RESOURCES


def get_resources():
    """Return a dictionary of registered resources."""
    return RESOURCES.copy()


def get_resource(identifier, fallback=None, default=MISSING):
    """Return the Resource object from the given identifier or default.

    Args:
        identifier (str): Identifier that has a registered resource
        fallback (str)[None]: Fallback identifier if the given identifier was not registered.
        default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
    """
    # Try finding the identifier
    try:
        return RESOURCES[identifier]
    except KeyError:
        pass

    # Try fallback
    try:
        if isinstance(fallback, Resource):
            return fallback
        return RESOURCES[fallback]
    except KeyError:
        pass

    # Check default
    if default is MISSING:
        raise ResourceNotAvailable('Resource "{}" not found'.format(identifier))
    return default


def get_binary(identifier, fallback=None, default=MISSING):
    """Return the binary data for the Resource object from the given identifier or default.

    Args:
        identifier (str): Identifier that has a registered resource
        fallback (str)[None]: Fallback identifier if the given identifier was not registered.
        default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
    """
    rsc = get_resource(identifier, fallback, default)
    if isinstance(rsc, Resource):
        return rsc.read_binary()
    return rsc


def get_text(identifier, fallback=None, default=MISSING, encoding='utf-8', errors='strict'):
    """Return the text data for the Resource object from the given identifier or default.

    Args:
        identifier (str): Identifier that has a registered resource
        fallback (str)[None]: Fallback identifier if the given identifier was not registered.
        default (object)[MISSING]: Default value to return if the identifier and fallback were not found.
        encoding (str)['utf-8']: Encoding to convert binary data to text.
        errors (str)['strict']: Error handling code when converting the binary data to text.
    """
    rsc = get_resource(identifier, fallback, default)
    if isinstance(rsc, Resource):
        return rsc.read_text(encoding=encoding, errors=errors)
    return rsc
