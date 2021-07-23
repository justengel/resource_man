============
resource_man
============


Standard Resource Functions

  * files - importlib.resources files this function is the standard for retrieving resources for Python 3.9+
  * as_file - context manager for retrieving a true filepath for Python 3.9+.
  * read_binary - Return the bytes found in the package with the given basename.
  * *read_text* - Return the text found in the pakcage with the given basename.
  * contents - Return an iterable of basenames in the given package.
  * is_resource - Return if the given package, basename exists.

Custom Helpers
  * register - Register a package and basename to an identifier. This can be overridden and used like a theme.
  * has_resource - Return if the given identifier has a registered resource.
  * get_resources - Return a dictionary of {identifier: Resource(package, name)}
  * get_resource - Return the Resource object for the given identifier, fallback, or default value.
  * get_binary - Return the binary data read from the found resource.
  * get_text - Return the text data read from teh found resource.


Resource Man Example
====================

Register and use identifiers.

.. code-block:: python

    # mylib/run.py
    # File Structure:
    #     mylib/
    #         __init__.py
    #         run.py
    #         actions/
    #             __init__.py
    #             edit-cut.png
    import resource_man

    resource_man.register('edit-cut', 'mylib.actions', 'edit-cut.png')

    if __name__ == '__main__':
        edit_cut_bin = resource_man.get_binary('edit-cut')


Qt Example
==========
The *importlib.resources* library prefers reading data from a resource instead of using filename paths.
This is to speed up execution and support with zip files.
The *resource_man* library includes a QIcon.
This QIcon can take in binary data as the first argument to create the icon.
This QIcon can also be created using *fromTheme* with a registered resource.
This library uses *QtPy* to support PySide or PyQt.


.. code-block:: python

    # mylib/run.py
    # File Structure:
    #     mylib/
    #         __init__.py
    #         run.py
    #         actions/
    #             __init__.py
    #             edit-cut.png
    import my_lib.actions  # Must import packages with subpackages that use importlib.resources
    from qtpy import QtWidgets
    from resource_man.qt import QIcon, register, get_binary, read_binary


    # Register package resources to an identifier that can be used with fromTheme
    # must import check_lib.check_sub for importlib.resources to work
    register('edit-cut', 'my_lib.actions', 'edit-cut.png')


    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        widg = QtWidgets.QWidget()
        widg.setLayout(QtWidgets.QVBoxLayout())
        widg.show()

        # Get icon from theme (resource_man register support)
        btn_theme = QtWidgets.QPushButton(QIcon.fromTheme('edit-cut'), 'Theme')
        widg.layout().addWidget(btn_theme)

        # resource_man binary
        btn_binary_resource_man = QtWidgets.QPushButton(QIcon(get_binary('edit-cut')), 'Binary resource_man')
        widg.layout().addWidget(btn_binary_resource_man)

        # importlib.resources binary
        btn_binary_importlib = QtWidgets.QPushButton(QIcon(read_binary('my_lib.actions', 'edit-cut.png')), 'importlib resource_man')
        widg.layout().addWidget(btn_binary_importlib)

        app.exec_()


importlib.resources Example
===========================

Using filenames and paths.
As stated earlier Python recommends that you use importlib.resources to read the resource data.
Filenames still have some support with importlib.resources, but it with the use of context manager.

.. code-block:: python

    # my_interface.py
    # sdl2 with sld2.dll in package
    # File Structure:
    #     my_sdl/
    #         sdl2_dll_path/
    #             SDL2.dll
    #         __init__.py
    #         my_interface.py
    import os
    from resource_man import files, as_file

    with as_file(files('my_sdl').joinpath('sdl2_dll_path/SDL2.dll')) as sdl_path:
        os.environ.setdefault('PYSDL2_DLL_PATH', os.path.dirname(str(sdl_path)))
        import sdl2

    # Use sdl2
    assert sdl2 is not None


PyInstaller Helper
==================

This library has a collect_datas helper function.
I believe this function to be more useful than PyInstallers built in tool.

.. code-block:: python

    # hook-mylib.py
    #
    # File Structure:
    #     mylib/
    #         __init__.py
    #         run.py
    #         edit-cut.png
    #     pyinstaller-hooks/
    #         hook-mylib.py
    from resource_man.pyinstaller import collect_datas

    datas = collect_datas('mylib')  # Will also find resources in sub packages


Use the pyinstaller helper with pylibimp to import all resources for your project.

.. code-block:: python

    # build_exe.py
    #
    # File Structure:
    #     mylib/
    #         __init__.py
    #         run.py
    #         edit-cut.png
    #     build_exe.py
    from resource_man.pyinstaller import collect_datas
    from PyInstaller import config
    from pylibimp import import_module
    import subprocess


    def get_dependent_modules(main_module):
        """Get the dependent modules from importing the main_module."""
        dependent_modules = {}
        import_module(main_module, reset_modules=True, dependent_modules=dependent_modules)
        return dependent_modules


    def get_datas(dependent_modules):
        """Return a list of command line arguments for pyinstaller to add data."""
        pyinstaller_args = []
        ignore_pkgs = ['PySide', 'PyQt', 'shiboken']  # PyInstaller properly includes resources for these
        for name in list(dependent_modules.keys()):
            if '.' in name:
                name = name.split('.', 1)[0]
            if name in ignore_pkgs:
                continue
            ignore_pkgs.append(name)
            with contextlib.suppress(ImportError, TypeError, ValueError, IndexError, Exception):
                datas = collect_datas(name)
                for data in datas:
                    pyinstaller_args.extend(['--add-data', os.pathsep.join(data)])

        return pyinstaller_args


    if __name__ == '__main__':
        main_module = 'mylib/run.py'
        modules = get_dependent_modules(main_module)
        args = get_datas(modules)

        subprocess.run(['pyinstaller', main_module] + args)
