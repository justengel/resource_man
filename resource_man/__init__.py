from .__meta__ import version as __version__

from .importlib_interface import \
    USING_IMPORTLIB, USING_IMPORTLIB_RESOURCES, USING_RESOURCE_MAN, Traversable, \
    files, as_file, read_binary, read_text, contents, is_resource, \
    rsc_files, rsc_as_file, rsc_read_binary, rsc_read_text, rsc_contents, rsc_is_resource
from .interface import ResourceNotAvailable, Resource, register, has_resource, get_resources, get_resource, \
    get_binary, get_text

try:
    from .pyinstaller import collect_datas, EXCLUDE_EXT, SOURCE_SUFFIXES
except (ImportError, Exception):
    pass

try:
    from .qt import QIcon
except (ImportError, Exception):
    pass
