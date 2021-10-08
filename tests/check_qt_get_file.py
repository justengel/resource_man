import os
from resource_man.qt import load_resource, register, Traversable, ResourceNotAvailable, get_resource
from qtpy import QtCore, QtWidgets


# Register on import outside of main
EDIT_CUT = register('check_lib.check_sub', 'edit-cut.png', None)  # None uses name no ext as alias ('edit-cut')
register('check_lib.check_sub', 'document-save-as.svg', None)  # None uses name no ext as alias ('document-save-as')
RSC = register('check_lib', 'rsc.txt', ...)  # ... uses name as alias ("rsc.txt")
RSC2 = register('check_lib.check_sub', 'rsc2.txt', ...)  # ... uses name as alias ("rsc2.txt")
DOCUMENT_NEW = register('check_lib.check_sub', 'document-new.png')  # QFile ":/check_lib/check_sub/document-new.png"

LOADED_COMPILED = False


def old_get_file(name, return_bytes=True, extension=None):
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


def check_resource():
    global LOADED_COMPILED
    from resource_man.qt import get_file

    assert old_get_file('document-save-as') == get_file('document-save-as')
    assert old_get_file('rsc.txt') == get_file('rsc.txt')
    assert old_get_file('rsc.txt') == get_file('rsc.txt')

    # Must
    if LOADED_COMPILED:
        assert old_get_file(':/rsc.txt', return_bytes=False) == get_file(':/rsc.txt', return_bytes=False)

    assert old_get_file('document-save-as', extension='.svg') == get_file('document-save-as', extension='.svg')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    LOADED_COMPILED = load_resource()  # Load the Qt RCC after QApplication

    check_resource()
