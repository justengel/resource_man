from dynamicmethod import dynamicmethod
from qtpy import QtGui
from .importlib_interface import \
    USING_IMPORTLIB, USING_IMPORTLIB_RESOURCES, USING_RESOURCE_MAN, Traversable, \
    files, as_file, read_binary, read_text, contents, is_resource
from .interface import ResourceNotAvailable, Resource, register, has_resource, get_resources, get_resource, \
    get_binary, get_text


__all__ = [
    'QIcon',
    'USING_IMPORTLIB', 'USING_IMPORTLIB_RESOURCES', 'USING_RESOURCE_MAN', 'Traversable',
    'files', 'as_file', 'read_binary', 'read_text', 'contents', 'is_resource',
    'ResourceNotAvailable', 'Resource', 'register', 'has_resource', 'get_resources', 'get_resource',
    'get_binary', 'get_text'
    ]


class QIcon(QtGui.QIcon):
    def __new__(cls, *args, **kwargs):
        pixmap = None
        if len(args) >= 1 and isinstance(args[0], bytes):
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(args[0])
            args = (pixmap, ) + args[1:]
        obj = super().__new__(cls, *args, **kwargs)
        obj._pixmap = pixmap
        return obj

    def __init__(self, *args, **kwargs):
        if len(args) >= 1 and isinstance(args[0], bytes):
            args = (self._pixmap, ) + args[1:]
        super().__init__(*args, **kwargs)

    @dynamicmethod  # Works as class or instance method
    def fromTheme(cls, name, fallback=None):
        self = cls
        if not isinstance(self, QIcon):
            self = cls()  # This is a class create the instance

        if has_resource(name) or has_resource(fallback):
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(get_binary(name, fallback))
            self.addPixmap(pixmap)
        elif fallback:
            QtGui.QIcon.fromTheme(self, name, fallback)
        else:
            QtGui.QIcon.fromTheme(self, name)
        return self
