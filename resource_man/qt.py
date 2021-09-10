import os
import sys
import argparse
import subprocess
from pathlib import Path
import importlib
from contextlib import contextmanager
from dynamicmethod import dynamicmethod
from qtpy import API_NAME, QtCore, QtGui, QtSvg

from resource_man.__meta__ import version as __version__
from resource_man.importlib_interface import \
    READ_API, FILES_API, Traversable, contents, is_resource, read_binary, read_text, files, as_file
from resource_man.interface import \
    ResourceNotAvailable, Resource, ResourceManager, get_global_manager, set_global_manager, temp_manager, \
    clear, register, register_directory, unregister, has_resource, get_resources, get_resource, get_binary, get_text


# Qt rcc compiler path
QT_RCC_BIN = files(API_NAME).joinpath('rcc.exe')
try:
    if 'PyQt' in API_NAME:
        # pyrcc5 binary
        QT_RCC_BIN = 'pyrcc' + ''.join(c for c in API_NAME if c.isdigit())
except (ValueError, Exception):
    pass


__all__ = [
    'get_file', 'QPixmap', 'QIcon', 'QSvgWidget', 'create_qrc', 'compile_qrc', 'create_compiled', 'load_resource',
    'compiled_py_to_qtpy',

    'READ_API', 'FILES_API', 'Traversable', 'contents', 'is_resource', 'read_binary', 'read_text', 'files', 'as_file',

    'ResourceNotAvailable', 'Resource', 'ResourceManager', 'get_global_manager', 'set_global_manager', 'temp_manager',
    'clear', 'register', 'register_directory', 'unregister', 'has_resource', 'get_resources', 'get_resource',
    'get_binary', 'get_text',
    '__version__'
    ]


def get_file(name, return_bytes=True, extension=None):
    """Return the Qt file name or binary data from the file.

    Args:
        name (str/bytes/Traversable/Resource): Find the file from the name or resource object.
        return_bytes (bool)[True]: If name is Traversable or Resource try reading the bytes.
            If False return Traversable.
        extension (str)[None]: If given str check the extension before returning a valid value.

    Returns:
        name (str/bytes/Traversable): Prefer returning the string filename.
            If unable to find the filename and return_bytes is True return the file bytes.
            If unable to find the filename and return_bytes is False return the Traversable (Path) object.
            If not found or the filename does not have the proper extension return ''.
    """
    if isinstance(name, bytes):
        return name
    elif isinstance(name, Traversable):
        has_extension = extension is None or os.path.splitext(str(name))[-1].lower() == extension.lower()
        if has_extension:
            if return_bytes:
                return name.read_bytes()
            return name  # Returning Traversable
        return ''

    # Try to create the icon from the Qt name
    try:
        has_extension = extension is None or os.path.splitext(str(name))[-1].lower() == extension.lower()
        if has_extension:
            if QtCore.QFile.exists(name):
                return name

            qt_name = ':/' + name
            if QtCore.QFile.exists(qt_name):
                return qt_name
    except (ResourceNotAvailable, TypeError, ValueError, Exception):
        pass

    # Try to create the icon from the registered resource name
    try:
        resource = get_resource(name)
        has_extension = extension is None or os.path.splitext(str(resource.name))[-1].lower() == extension.lower()
        if has_extension:
            rsc_name = resource.alias
            qt_name = ':/' + rsc_name
            if QtCore.QFile.exists(rsc_name):
                return rsc_name
            elif QtCore.QFile.exists(qt_name):
                return qt_name

            # Last resort return the binary.
            if return_bytes:
                return resource.read_bytes()
            return resource.files()  # Returning Traversable
    except (ResourceNotAvailable, TypeError, ValueError, OSError, ImportError, Exception):
        pass

    return ''


QtGui_QIcon = QtGui.QIcon
QtGui_QPixmap = QtGui.QPixmap


class QPixmap(QtGui_QPixmap):
    """Special QPixmap that can load from resource_man values."""
    def __new__(cls, *args, **kwargs):
        return super(QPixmap, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        load_data = None
        if len(args) >= 1 and isinstance(args[0], (Resource, str, bytes, Traversable)):
            # Try to find filename, Qt File, or importlib.resources read resource bytes.
            data_file = get_file(args[0], return_bytes=True, extension=None)
            if isinstance(data_file, str):
                args = (data_file,) + args[1:]
            elif isinstance(data_file, bytes):
                load_data = data_file
                args = ('',) + args[1:]

        super(QPixmap, self).__init__(*args, **kwargs)

        if isinstance(load_data, bytes):
            self.loadFromData(load_data)


class QIcon(QtGui_QIcon):
    """Special QIcon that can load from resource_man values."""
    def __new__(cls, *args, **kwargs):
        return super(QIcon, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        is_valid = False
        if len(args) >= 1:
            if isinstance(args[0], str) and QIcon.hasThemeIcon(args[0]):
                args = (QtGui_QIcon.fromTheme(args[0]),) + args[1:]
                is_valid = True
            elif isinstance(args[0], (Resource, str, bytes, Traversable)):
                # Try to find filename, Qt File, or importlib.resources read resource bytes.
                data_file = get_file(args[0], return_bytes=True, extension=None)
                if isinstance(data_file, str):
                    args = (data_file,) + args[1:]
                    is_valid = True
                elif isinstance(data_file, bytes):
                    pixmap = QtGui_QPixmap()
                    pixmap.loadFromData(data_file)
                    args = (pixmap, ) + args[1:]
                    is_valid = True

        super(QIcon, self).__init__(*args, **kwargs)
        self.is_valid = is_valid

    @dynamicmethod
    def fromTheme(self, name, fallback=None):
        icn = QIcon(name)
        if not icn.is_valid and fallback is not None:
            icn = QIcon(fallback)

        if isinstance(self, QIcon):
            self.swap(icn)
            return self
        return icn


class QSvgWidget(QtSvg.QSvgWidget):
    """QSvgWidget with resource_man support."""
    def __new__(cls, *args, **kwargs):
        return super(QSvgWidget, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        load_data = None
        if len(args) >= 1 and isinstance(args[0], (Resource, str, bytes, Traversable)):
            # Try to find filename, Qt File, or importlib.resources read resource bytes.
            data_file = get_file(args[0], return_bytes=True, extension='.svg')
            if isinstance(data_file, str):
                args = (data_file,) + args[1:]
            elif isinstance(data_file, bytes):
                load_data = data_file
                args = ('',) + args[1:]

        super(QSvgWidget, self).__init__(*args, **kwargs)

        if isinstance(load_data, bytes):
            self.load(load_data)


@contextmanager
def context_file(file):
    """Use as_file or just yield the given file."""
    if isinstance(file, Traversable):
        with as_file(file) as fname:
            yield fname
    else:
        yield file


def create_qrc(filename="resource_man_compiled_resources.qrc", prefix='', resource_manager=None, main_module=None):
    """Make a Qt RCC file.

    Note:
        This registers the resource with an alias shortcut identifier.

        .. code-block:: python

            >>> resource_man.register('check_lib.check_sub', 'edit-cut.png', alias='edit-cut')

        The alias can be used with QIcon(":/edit-cut")

    Example:
        .. code-block:: python

            >>> import resource_man.qt as resource_man
            >>>
            >>> resource_man.register('check_lib.check_sub', 'edit-cut.png', 'edit-cut')
            >>>
            >>> resource_man.create_qrc()  # app_resources.qrc created

    Args:
        filename (str)['resource_man_compiled_resources.qrc']: Filename to create the .qrc file with.
        prefix (str)['']: qresource prefix.
        resource_manager (ResourceManager)[None]: Resource manger to use. If None use default global ResourceManager.
        main_module (str)[None]: This module will be imported to register resources before creating the .qrc file.

    Returns:
        filename (str): Absolute path of the filename that was written.
    """
    if resource_manager is None:
        resource_manager = get_global_manager()

    # Import the main module that registers the resources
    if isinstance(main_module, (str, Path)):
        main_module = str(main_module)
        if '/' in main_module or '\\' in main_module or '.' in main_module:
            sys.path.append(os.path.dirname(main_module))
            main_module = os.path.splitext(os.path.basename(main_module))[0]
        importlib.import_module(main_module)

    # Create the QRC File
    text = ['<!DOCTYPE RCC><RCC version="1.0">']
    if prefix:
        text.append('<qresource prefix="{}">'.format(prefix))
    else:
        text.append('<qresource>')

    for resource in resource_manager.get_resources():
        if resource.is_resource():
            with resource.as_file() as rsc_file:
                text.append('\t<file alias="{}">{}</file>'.format(resource.alias, os.path.relpath(str(rsc_file))))

    text.append('</qresource>')
    text.append('</RCC>')

    with open(filename, "w") as file:
        file.write("\n".join(text))

    return os.path.abspath(filename)


def compile_qrc(filename="resource_man_compiled_resources.qrc", output=None, rcc_bin=QT_RCC_BIN, use_qtpy=True):
    """Create the python resource file from the .qrc file.

    Args:
        filename (str)['resource_man_compiled_resources.qrc']: QRC resrouce file.
        output (str)[None]: Name of the new python file that should be created.
            Default "resource_man_compiled_resources.py" or "resource_man_compiled_resources.rcc".
        rcc_bin (Traversable/Path/str)[files(API_NAME).joinpath(rcc.exe)]: Path to the rcc binary.
        use_qtpy (bool)[True]: If True replace the Qt API with qtpy.

    Returns:
        filename (str): Python filename of the saved resource file.
    """
    if output is None:
        output = os.path.splitext(filename)[0] + ".py"  # or .py and "import app_resources.py"

    with context_file(rcc_bin) as rcc:
        rcc = str(rcc)
        args = [rcc, filename, '-o', output]
        is_py = not output.endswith('.rcc')
        is_pyqt = 'pyrcc' in rcc
        is_pyside = not is_pyqt

        if is_py and is_pyside:  # If .py file and PySide you need "-g python" arguments
            args.extend(['-g', 'python'])
        elif not is_py and is_pyside:
            # .rcc binary file for pyside
            args.append('-binary')
        elif not is_py and is_pyqt:
            # .rcc binary file for PyQt is not supported
            args[3] = output = os.path.splitext(output)[0] + '.py'  # PyQT rcc does not support rcc binary

        success = subprocess.run(args, stdout=sys.stdout, stderr=sys.stderr).returncode == 0
        if success and is_py and use_qtpy:
            compiled_py_to_qtpy(output)

        return success


def compiled_py_to_qtpy(filename):
    """Modify the compiled .py file to use qtpy instead of PySide2 or PyQt5."""
    # Convert resources.py import of PySide2 or PyQt5 to qtpy
    with open(filename, 'r+') as f:
        lines = f.readlines()
        f.seek(0, 0)
        f.truncate()  # File size is not different must truncate

        # Cannot use f.read().replace(API_NAME, 'qtpy') because we allow given rcc_bin
        for i, line in enumerate(lines):
            if ' import QtCore' in line:  # line is "from PySide2 import QtCore"
                lines[i] = 'from qtpy import QtCore\n'  # Does not use Windows \r\n. Otherwise could use os.linesep
                break

        f.writelines(lines)


def create_compiled(filename="resource_man_compiled_resources.qrc", prefix='', main_module=None, output=None,
                    rcc_bin=QT_RCC_BIN, use_qtpy=True):
    """Make a Qt RCC .qrc file, compile the Qt RCC file to a .py or .rcc file, and remove the unneeded QRC file.

    Note:
        This registers the resource with an alias shortcut identifier.

        .. code-block:: python

            >>> resource_man.register('check_lib.check_sub', 'edit-cut.png', 'edit-cut')

        The alias can be used with QIcon(":/edit-cut")

    Example:
        .. code-block:: python

            >>> import resource_man.qt as resource_man
            >>>
            >>> resource_man.register('check_lib.check_sub', 'edit-cut.png', 'edit-cut')
            >>>
            >>> resource_man.create_qrc()  # resource_man_compiled_resources.qrc created
            >>> resource_man.compile_qrc()  # resource_man_compiled_resources.py created
            >>> os.remove('resource_man_compiled_resources.qrc')

    Args:
        filename (str)['resource_man_compiled_resources.qrc']: Filename to create the .qrc file with.
        prefix (str)['']: qresource prefix.
        main_module (str)[None]: This module will be imported to register resources before creating the .qrc file.
        output (str)[None]: Name of the new python file that should be created.
            Default "resource_man_compiled_resources.py" or "resource_man_compiled_resources.rcc".
        rcc_bin (Traversable/Path/str)[files(API_NAME).joinpath(rcc.exe)]: Path to the rcc binary.
        use_qtpy (bool)[True]: If True replace the Qt API with qtpy.

    Returns:
        filename (str): Python filename of the saved resource file.
    """
    create_qrc(filename, prefix=prefix, main_module=main_module)
    out = compile_qrc(filename, output=output, rcc_bin=rcc_bin, use_qtpy=use_qtpy)
    os.remove(filename)
    return out


def load_resource(filename='resource_man_compiled_resources.py'):
    """Load a Qt resource file."""
    try:
        if filename == 'resource_man_compiled_resources.py':
            import resource_man_compiled_resources
            return True
    except (ImportError, Exception):
        pass

    try:
        # Try to use a resource file path
        with context_file(filename) as fname:
            fname = str(fname)
            if fname.endswith('.rcc'):
                return QtCore.QResource.registerResource(fname)
            else:
                directory = os.path.dirname(fname)
                dir_added = directory not in sys.path  # Could convert to := later. Want to support backwards compatible
                if dir_added:
                    sys.path.append(directory)
                try:
                    importlib.import_module(os.path.splitext(os.path.basename(fname))[0])
                finally:
                    if dir_added:
                        sys.path.remove(directory)
                return True
    except (ImportError, Exception):
        return False


if __name__ == '__main__':
    P = argparse.ArgumentParser('Run a Qt resource helper.')

    # ===== Sub commands =====
    SUBP = P.add_subparsers(help='Qt Resource commands.')

    # Create QRC
    CREATE_QRC = SUBP.add_parser('create', help='Create the .qrc file.')
    CREATE_QRC.set_defaults(func=create_qrc)
    # Main module to import
    CREATE_QRC.add_argument('main_module', type=str, help='Main module that is imported and registers resources.')
    CREATE_QRC.add_argument('--filename', '-f', type=str, default='resource_man_compiled_resources.qrc')
    CREATE_QRC.add_argument('--prefix', '-p', type=str, default='')

    # Compile QRC
    COMPILE_QRC = SUBP.add_parser('compile', help='Compile the .qrc file into an importable .py file of binaries.')
    COMPILE_QRC.set_defaults(func=compile_qrc)
    COMPILE_QRC.add_argument('--filename', '-f', type=str, default='resource_man_compiled_resources.qrc')
    COMPILE_QRC.add_argument('--output', '-o', type=str, default=None)
    COMPILE_QRC.add_argument('--rcc_bin', type=str, default=QT_RCC_BIN)
    COMPILE_QRC.add_argument('--use_qtpy', '-q', type=bool, default=True, help='Convert compiled resources to qtpy.')

    # Run both
    RUN_P = SUBP.add_parser('run', help='Create and compile the resources.')
    RUN_P.set_defaults(func=create_compiled)
    # Main module to import
    RUN_P.add_argument('main_module', type=str, help='Main module that is imported and registers resources.')
    RUN_P.add_argument('--filename', '-f', type=str, default='resource_man_compiled_resources.qrc')
    RUN_P.add_argument('--prefix', '-p', type=str, default='')
    RUN_P.add_argument('--output', '-o', type=str, default=None)
    RUN_P.add_argument('--rcc_bin', type=str, default=QT_RCC_BIN)
    RUN_P.add_argument('--use_qtpy', '-q', type=bool, default=True, help='Convert compiled resources to qtpy.')

    # ===== Parse given command line arguments into keyword arguments =====
    ARGS, REMAIN = P.parse_known_args()
    KWARGS = {name: getattr(ARGS, name, None) for name in dir(ARGS) if not name.startswith('_')}

    # ===== Run the subcommand =====
    FUNC = KWARGS.pop('func')
    FUNC(**KWARGS)
