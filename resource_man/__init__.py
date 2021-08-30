from .__meta__ import version as __version__

from .importlib_interface import \
    READ_API, FILES_API, Traversable, contents, is_resource, read_binary, read_text, files, as_file, \
    rsc_files, rsc_as_file, rsc_read_binary, rsc_read_text, rsc_contents, rsc_is_resource

from .interface import \
    ResourceNotAvailable, Resource, ResourceManager, get_global_manager, set_global_manager, temp_manager, \
    register, has_resource, get_resources, get_resource, get_binary, get_text

