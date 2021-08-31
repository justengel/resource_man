import check_lib.check_sub
from qtpy import QtWidgets, QtCore
import resource_man.qt as rsc


# Register on import outside of main
RSC = rsc.register('check_lib', 'rsc.txt', ...)  # ... uses name as alias ("rsc.txt")
RSC2 = rsc.register('check_lib.check_sub', 'rsc2.txt', ...)  # ... uses name as alias ("rsc2.txt")
EDIT_CUT = rsc.register('check_lib.check_sub', 'edit-cut.png', alias='edit-cut')
DOCUMENT_NEW = rsc.register('check_lib.check_sub', 'document-new.png')  # QFile ":/check_lib/check_sub/document-new.png"


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # Load the Qt RCC after QApplication
    success = rsc.load_resource()

    widg = QtWidgets.QWidget()
    widg.setLayout(QtWidgets.QVBoxLayout())

    # Resource file (Must be compiled and loaded)
    file = QtCore.QFile(':/rsc2.txt')
    if not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
        text = 'File Not Available'
    else:
        text = file.readAll().data().decode('utf-8')
        file.close()
    msg = 'READ FILE\n' \
          'File Path = {}\nread_text = {}\nQFile :/rsc2.txt = {}'.format(str(RSC2), repr(RSC2.read_text()), repr(text))
    lbl = QtWidgets.QLabel(msg)
    widg.layout().addWidget(lbl)

    # Use resource_man register alias
    btn = QtWidgets.QPushButton(rsc.QIcon('edit-cut'), 'resource_man alias "edit-cut"', None)
    widg.layout().addWidget(btn)

    # Use Qt QResource alias name
    btn = QtWidgets.QPushButton(rsc.QIcon(':/edit-cut'), 'QFile alias ":/edit-cut"', None)
    widg.layout().addWidget(btn)

    # Use Qt QResource File name - DOES NOT WORK! CAN ONLY USE QRC ALIAS IDENTIFIER!
    # btn = QtWidgets.QPushButton(QIcon(':\\check_lib\\check_sub\\edit-cut.png'),
    #                                   'QFile name ":\\check_lib\\check_sub\\edit-cut.png"', None)
    # widg.layout().addWidget(btn)

    # Use resource_man register alias
    btn = QtWidgets.QPushButton(rsc.QIcon(DOCUMENT_NEW), 'resource_man object DOCUMENT_NEW', None)
    widg.layout().addWidget(btn)

    # Use Qt QResource File name alias
    btn = QtWidgets.QPushButton(rsc.QIcon(':/check_lib/check_sub/document-new.png'), 'QFile alias ":/check_lib/check_sub/document-new.png"', None)
    widg.layout().addWidget(btn)

    # Use Qt QResource File name alias - DOES NOT WORK! CAN ONLY USE QRC ALIAS IDENTIFIER!
    # btn = QtWidgets.QPushButton(rsc.QIcon(':/check_lib/check_sub/document-new.png'),
    #                                   '":/check_lib/check_sub/document-new.png"', None)
    # widg.layout().addWidget(btn)

    # ===== The two methods below only work if the resource files exist in the executable =====
    # you need to include the .png files as data files in PyInstaller
    # you also need to import the package (`import check_lib.check_sub`) for PyInstaller to include the package.

    # resource_man binary (resource_man register alias support)
    try:
        btn_binary_resource_man = QtWidgets.QPushButton(rsc.QIcon(rsc.get_binary('edit-cut')), 'resource_man get_binary("edit-cut")')
        widg.layout().addWidget(btn_binary_resource_man)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass

    # importlib.resources binary
    try:
        btn_binary_importlib = QtWidgets.QPushButton(rsc.QIcon(rsc.read_binary('check_lib.check_sub', 'edit-cut.png')),
                                                     'importlib.resources read_binary("check_lib.check_sub", "edit-cut.png")')
        widg.layout().addWidget(btn_binary_importlib)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass
    try:
        lbl = QtWidgets.QLabel()
        lbl.setPixmap(rsc.QPixmap(rsc.files('check_lib.check_sub').joinpath('edit-cut.png')).scaled(24, 24, QtCore.Qt.KeepAspectRatio))
        widg.layout().addWidget(lbl)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass

    widg.show()
    app.exec_()
