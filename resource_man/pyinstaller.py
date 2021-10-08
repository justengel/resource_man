import os
import types
import contextlib

try:
    from importlib.machinery import SOURCE_SUFFIXES
except (ImportError, Exception):
    SOURCE_SUFFIXES = ['.py', '.pyw', '.py2', '.py3']

from resource_man.__meta__ import version as __version__
from resource_man.importlib_interface import \
    READ_API, FILES_API, Traversable, contents, is_resource, read_binary, read_text, files, as_file
from resource_man.interface import \
    ResourceNotAvailable, Resource, ResourceManager, get_global_manager, set_global_manager, temp_manager, \
    add_manager, remove_manager, clear, register, register_directory, unregister, has_resource, \
    get_resources, get_resource, get_binary, get_text, \
    MISSING


__all__ = [
    'registered_datas', 'find_datas', 'EXCLUDE_EXT', 'SOURCE_SUFFIXES',

    'READ_API', 'FILES_API', 'Traversable', 'contents', 'is_resource', 'read_binary', 'read_text', 'files', 'as_file',

    'ResourceNotAvailable', 'Resource', 'ResourceManager', 'get_global_manager', 'set_global_manager', 'temp_manager',
    'add_manager', 'remove_manager', 'clear', 'register', 'register_directory', 'unregister', 'has_resource',
    'get_resources', 'get_resource', 'get_binary', 'get_text',
    'MISSING',
    '__version__'
    ]


def registered_datas(resource_manager=None):
    """Return a list of datas that were registered.

    Args:
        resource_manager (ResourceManager)[None]: Resource manger to use. If None use default global ResourceManager.

    Returns:
        datas (list): List of (existing file path, rel install path).
    """
    if resource_manager is None:
        resource_manager = get_global_manager()

    datas = []

    for resource in resource_manager.get_resources():
        if resource.is_resource():
            with resource.as_file() as rsc_file:
                data = (os.path.relpath(str(rsc_file)), os.path.dirname(resource.package_path))
                datas.append(data)

    return datas


EXCLUDE_EXT = SOURCE_SUFFIXES + ['.pyc', '.pyd']


def find_datas(package, exclude_ext=None, **kwargs):
    """Collect data files for pyinstaller.

    Args:
        package (types.ModuleType/str/Traversable): Top level package module or module name.
        exclude_ext (list)[None]: List of extensions to not include in the pyinstaller data.

    Returns:
        datas (list): List of (abs file path, rel install path). This will also include subdirectories.
    """
    if exclude_ext is None:
        exclude_ext = EXCLUDE_EXT

    datas = []
    pkg_name = package
    if isinstance(package, types.ModuleType):
        pkg_name = package.__package__

    with contextlib.suppress(ImportError, Exception):
        toplvl = files(package)
        with as_file(toplvl) as n:
            toplvl_filename = str(n)  # n should be a Path object, but I noticed it was a str anyway
        subdirs = [toplvl]
        while True:
            try:
                directory = subdirs.pop(0)
            except IndexError:
                break

            for path in directory.iterdir():
                if path.name == '__pycache__':
                    continue

                if path.is_dir():
                    # Add subpackage
                    subdirs.append(path)
                elif path.suffix not in exclude_ext:
                    # Assume this is a resource.
                    with as_file(path) as filename:
                        try:
                            filename = str(filename.resolve())
                        except (AttributeError, Exception):
                            pass
                        relpath = os.path.join(pkg_name, os.path.relpath(filename, toplvl_filename))
                        data = (filename, os.path.dirname(relpath))
                        if data not in datas:
                            datas.append(data)

    return datas
