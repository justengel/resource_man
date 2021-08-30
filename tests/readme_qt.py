from qtpy import QtWidgets, QtCore
from resource_man.qt import QPixmap, QIcon, register, load_resource, \
    files, ResourceNotAvailable, get_binary, read_binary
import check_lib.check_sub

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
    except (ResourceNotAvailable, OSError, TypeError) as err:
        pass

    # importlib.resources binary
    try:
        btn_binary_importlib = QtWidgets.QPushButton(QIcon(read_binary('check_lib.check_sub', 'edit-cut.png')),
                                                     'importlib.resources read_binary("check_lib.check_sub", "edit-cut.png")')
        widg.layout().addWidget(btn_binary_importlib)
    except (ResourceNotAvailable, OSError, TypeError) as err:
        pass
    try:
        lbl = QtWidgets.QLabel()
        lbl.setPixmap(QPixmap(files('check_lib.check_sub').joinpath('edit-cut.png')).scaled(24, 24, QtCore.Qt.KeepAspectRatio))
        widg.layout().addWidget(lbl)
    except (ResourceNotAvailable, OSError, TypeError) as err:
        pass

    widg.show()
    app.exec_()
