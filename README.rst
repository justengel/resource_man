============
resource_man
============

Resource manager to work with Python standards and executables.

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

Register and use identifiers. This example requires that the file exists.
If you use PyInstaller to make an executable "mylib/actions/edit-cut.png" need to be included in datas.
This should also work if the resource is bundled in a zip file according to some of the Python documentation.

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


Best practice is probably to register the resource file in the __init__.py that it exists with.
Then you have access to all resources on import.

.. code-block:: python

    # mylib/actions/__init__.py
    import resource_man

    edit_cut = resource_man.register('edit-cut', 'mylib.actions', 'edit-cut.png')

    if __name__ == '__main__':
         edit_cut_bin = edit_cut.read_binary()

    # Use with `import mylib.actions`


importlib.resources Example
===========================

Using filenames and paths.
As stated earlier Python recommends that you use importlib.resources to read the resource data.
Filenames still have some support with importlib.resources, but it must be used as a context manager.

.. code-block:: python

    # my_interface.py
    # sdl2 with sld2.dll in package
    # File Structure:
    #     my_sdl/
    #         sdl2_dll_path/
    #             # __init__.py was required for pkg_resources. Do not know if it is still needed.
    #             __init__.py
    #             SDL2.dll
    #         __init__.py
    #         my_interface.py
    import os
    from resource_man import files, as_file
    import my_sdl.sdl2_dll_path  # Required for PyInstaller to include the package

    # ".sdl2_dll_path" would require __init__.py
    binary = files('my_sdl.sdl2_dll_path').joinpath('SDL2.dll').read_binary()

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
    from resource_man.pyinstaller import find_datas, registered_datas

    # datas = find_datas('mylib')  # Will also find resources in sub packages
    datas = registered_datas()  # Return a list of registered resources


Use the pyinstaller helper with pylibimp to import all resources for your project.

.. code-block:: python

    # build_exe.py
    from resource_man.pyinstaller import registered_datas
    from PyInstaller import config
    from pylibimp import import_module
    import subprocess

    if __name__ == '__main__':
        main_module = 'mylib/run.py'

        # Import the main module to register all of the data files.
        import_module(main_module, reset_modules=True)

        # Get registered datas
        datas = registered_datas()
        args = []
        for data in datas:
            args.extend(['--add-data', os.pathsep.join(data)])

        subprocess.run(['pyinstaller', main_module] + args)

You could also make your own PyInstaller hook using these helper functions.


Qt Example
==========
The *importlib.resources* library prefers reading data from a resource instead of using filename paths.
This is to speed up execution and support with zip files.
Qt Primarily uses filenames, but also has it's own system of importing compiled resources.
I have created several utilities to help with this.


Compiled Resources
~~~~~~~~~~~~~~~~~~
The best way is probably to use compiled resources.

The `resource_man` library helps with utilities for registering resources, create .qrc files, and compiling .qrc files.

**1. Register the Resource**

Use `resource_man` to register resources when the file is imported.

.. code-block:: python

    # main_qt.py
    # File Structure:
    #    main_qt.py
    #    check_lib/
    #        __init__.py
    #        check_sub/
    #            __init__.py
    #            edit-cut.png
    from resource_man.qt import register, get_binary, read_binary, load_resource, ResourceNotAvailable

    # Register on import outside of main
    register('edit-cut', 'check_lib.check_sub', 'edit-cut.png')
    register('document-new.png', 'check_lib.check_sub', 'document-new.png')

After registering, `resource_man` can create the list of resources in a .qrc file.

**2. Create .qrc File**

Create the .qrc file that can compile all resources into a binary data file.

.. code-block:: bat

    python -m resource_man.qt create ./main_qt.py

This creates a file that looks like.

.. code-block:: text

    <!DOCTYPE RCC><RCC version="1.0">
    <qresource>
        <file alias="edit-cut">check_lib\check_sub\edit-cut.png</file>
        <file alias="document-new.png">check_lib\check_sub\document-new.png</file>
    </qresource>
    </RCC>

**3. Compile the .qrc file**

Compile the .qrc file into an importable .py file. PySide can also make a C++ .rcc file that can be registered as well.

.. code-block:: bat

    python -m resource_man.qt compile

This creates a large .py file with the binary data.

**4. Load the compiled file**

Load the compiled .py file.

.. code-block:: python

    ...

    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        # Load the Qt RCC after QApplication
        success = load_resource()

**5. Use the qrc resource**

Use the QIcon or QPixmap to use the registered resource.

.. code-block:: python

    from resource_man.qt import QIcon, QPixmap

    ...

    icon = QIcon('edit-cut')
    icon = QIcon(':/edit-cut')
    icon = QIcon(':/document-new.png')

Use with importlib.resources.

.. code-block:: python

    from resource_man.qt import read_binary
    import check_lib.check_sub
    ...

    # Need to --add-datas with PyInstaller to use this in an executable
    binary_img = read_binary('check_lib.check_sub', 'edit-cut.png')


Full Example
~~~~~~~~~~~~

The *resource_man* library includes a QIcon and QPixmap class to use registered resources.
This QIcon and QPixmap can take in binary data as the first argument to create the icon.
This QIcon and QPixmap can also take the registered identifier.
This library uses *QtPy* to support PySide or PyQt.


.. code-block:: python

    # mylib/run.py
    # File Structure:
    #     check_lib/
    #         __init__.py
    #         run.py
    #         check_sub/
    #             __init__.py
    #             edit-cut.png
    #             document-new.png
    import check_lib.check_sub  # Must import packages with subpackages that use importlib.resources
    from qtpy import QtWidgets, QtCore
    from resource_man.qt import QPixmap, QIcon, register, load_resource, \
        files, ResourceNotAvailable, get_binary, read_binary


    # Register on import outside of main
    register('edit-cut', 'check_lib.check_sub', 'edit-cut.png')
    register('document-new.png', 'check_lib.check_sub', 'document-new.png')


    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        # Load the Qt RCC after QApplication
        success = load_resource()

        widg = QtWidgets.QWidget()
        widg.setLayout(QtWidgets.QVBoxLayout())

        # Use resource_man register identifier
        btn = QtWidgets.QPushButton(QIcon('edit-cut'), 'resource_man identifier "edit-cut"', None)
        widg.layout().addWidget(btn)

        # Use Qt QResource alias name
        btn = QtWidgets.QPushButton(QIcon(':/edit-cut'), 'QFile alias ":/edit-cut"', None)
        widg.layout().addWidget(btn)

        # Use Qt QResource File name - DOES NOT WORK! CAN ONLY USE QRC ALIAS IDENTIFIER!
        # btn = QtWidgets.QPushButton(QIcon(':\\check_lib\\check_sub\\edit-cut.png'),
        #                                   'QFile name ":\\check_lib\\check_sub\\edit-cut.png"', None)
        # widg.layout().addWidget(btn)

        # Use resource_man register identifier
        btn = QtWidgets.QPushButton(QIcon('document-new.png'), 'resource_man identifier "document-new.png"', None)
        widg.layout().addWidget(btn)

        # Use Qt QResource File name alias
        btn = QtWidgets.QPushButton(QIcon(':/document-new.png'), 'QFile alias ":/document-new.png"', None)
        widg.layout().addWidget(btn)

        # Use Qt QResource File name alias - DOES NOT WORK! CAN ONLY USE QRC ALIAS IDENTIFIER!
        # btn = QtWidgets.QPushButton(QIcon(':/check_lib/check_sub/document-new.png'),
        #                                   '":/check_lib/check_sub/document-new.png"', None)
        # widg.layout().addWidget(btn)

        # ===== The two methods below only work if the resource files exist in the executable =====
        # you need to include the .png files as data files in PyInstaller
        # you also need to import the package (`import check_lib.check_sub`) for PyInstaller to include the package.

        # resource_man binary (resource_man register support)
        try:
            btn_binary_resource_man = QtWidgets.QPushButton(QIcon(get_binary('edit-cut')), 'resource_man get_binary("edit-cut")')
            widg.layout().addWidget(btn_binary_resource_man)
        except (ResourceNotAvailable, OSError) as err:
            pass

        # importlib.resources binary
        try:
            btn_binary_importlib = QtWidgets.QPushButton(QIcon(read_binary('check_lib.check_sub', 'edit-cut.png')),
                                                         'importlib.resources read_binary("check_lib.check_sub", "edit-cut.png")')
            widg.layout().addWidget(btn_binary_importlib)
        except (ResourceNotAvailable, OSError) as err:
            pass
        try:
            lbl = QtWidgets.QLabel()
            lbl.setPixmap(QPixmap(files('check_lib.check_sub').joinpath('edit-cut.png')).scaled(24, 24, QtCore.Qt.KeepAspectRatio))
            widg.layout().addWidget(lbl)
        except (ResourceNotAvailable, OSError) as err:
            pass

        widg.show()
        app.exec_()
