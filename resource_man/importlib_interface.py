import os
import sys
import contextlib
import inspect
from pathlib import Path

USING_IMPORTLIB = False
USING_IMPORTLIB_RESOURCES = False
USING_RESOURCE_MAN = False

try:
    from importlib.resources import files, as_file, read_text, read_binary, contents, is_resource
    from importlib.abc import Traversable
    USING_IMPORTLIB = True
except (ImportError, Exception):
    try:
        from importlib_resources import files, as_file, read_text, read_binary, contents, is_resource
        from importlib_resources.abc import Traversable
        USING_IMPORTLIB_RESOURCES = True
    except (ImportError, Exception):
        files = None
        as_file = None
        read_text = None
        read_binary = None
        contents = None
        is_resource = None
        Traversable = Path


__all__ = [
    'USING_IMPORTLIB', 'USING_IMPORTLIB_RESOURCES', 'USING_RESOURCE_MAN', 'Traversable',
    'files', 'as_file', 'read_binary', 'read_text', 'contents', 'is_resource',
    'rsc_files', 'rsc_as_file', 'rsc_read_binary', 'rsc_read_text', 'rsc_contents', 'rsc_is_resource'
    ]


def rsc_files(module):
    if isinstance(module, str):
        if '.' in module:
            # Import the top level package and manually add a directory for each "."
            toplvl, remain = module.split('.', 1)
        else:
            toplvl, remain = module, ''

        # Get or import the module
        try:
            module = sys.modules[toplvl]
            path = Path(inspect.getfile(module))
        except (KeyError, Exception):
            try:
                module = __import__(toplvl)
                path = Path(inspect.getfile(module))
            except (ImportError, Exception):
                module = toplvl
                path = Path(module)

        # Get the path of the module
        if path.with_suffix('').name == '__init__':
            path = path.parent

        # Find the path from the top level module
        for pkg in remain.split('.'):
            path = path.joinpath(pkg)
    else:
        path = Path(inspect.getfile(module))
    if path.with_suffix('').name == '__init__':
        path = path.parent
    return path


@contextlib.contextmanager
def rsc_as_file(path):
    p = path
    if (isinstance(p, str) and not os.path.exists(p)) or (isinstance(p, (Path, Traversable)) and not p.exists()):
        p = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), str(path))
    if (isinstance(p, str) and not os.path.exists(p)) or (isinstance(p, (Path, Traversable)) and not p.exists()):
        p = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), '', str(path))

    yield Path(p)  # Documentation says should be Path object, but I noticed it was a string.


def rsc_read_binary(package, resource):
    """Return the binary contents of the resource."""
    return files(package).joinpath(resource).read_bytes()


def rsc_read_text(package, resource, encoding='utf-8', errors='strict'):
    """Return the decoded string of the resource.

    The decoding-related arguments have the same semantics as those of
    bytes.decode().
    """
    return files(package).joinpath(resource).read_text(encoding, errors)


def rsc_contents(package):
    """Return an iterable of entries in 'package'.

    Note that not all entries are resources.  Specifically, directories are
    not considered resources.  Use `is_resource()` on each entry returned here
    to check if it is a resource or not.
    """
    return iter([p.name for p in files(package).iterdir()])


def rsc_is_resource(package, name):
    """True if 'name' is a resource inside 'package'.

    Directories are *not* resources.
    """
    package = files(package)
    if package.joinpath(name).exists() and not package.joinpath(name).is_dir():
        return True
    try:
        package_contents = set(contents(package))
    except (NotADirectoryError, FileNotFoundError):
        return False
    if name not in package_contents:
        return False
    # Just because the given file_name lives as an entry in the package's
    # contents doesn't necessarily mean it's a resource.  Directories are not
    # resources, so let's try to find out if it's a directory or not.
    path = Path(package.__spec__.origin).parent / name
    return path.is_file()


if files is None:
    files = rsc_files
    as_file = rsc_as_file
    read_text = rsc_read_text
    read_binary = rsc_read_binary
    contents = rsc_contents
    is_resource = rsc_is_resource
    USING_RESOURCE_MAN = True
