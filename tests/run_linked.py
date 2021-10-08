"""Run qt compile for multiple managers."""
import check_lib.check_sub
from qtpy import QtWidgets, QtCore
import resource_man.qt as rsc

RMAN2 = rsc.ResourceManager(prefix='rman2')
rsc.add_manager(RMAN2)

# Register on import outside of main
rsc.register('check_lib.check_sub', 'edit-cut.png', None)  # None uses name no ext as alias ('edit-cut')
rsc.register('check_lib.check_sub', 'document-save-as.svg', None)  # None uses name no ext as alias ('document-save-as')
rsc.register('check_lib', 'rsc.txt', ...)  # ... uses name as alias ("rsc.txt")
rsc.register('check_lib.check_sub', 'document-new.png')  # QFile ":/check_lib/check_sub/document-new.png"

# Check rman2 prefix
RMAN2.register('check_lib.check_sub', 'document-save-as.svg', 'document-save-as2')
RMAN2.register('check_lib.check_sub', 'rsc2.txt', ...)  # ... uses name as alias (":/rman2/rsc2.txt")
RMAN2.register('check_lib.check_sub', 'document-new.png')  # QFile ":/rman2/check_lib/check_sub/document-new.png"


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # Load the Qt RCC after QApplication
    success = rsc.load_resource()

    widg = QtWidgets.QWidget()
    widg.setLayout(QtWidgets.QVBoxLayout())

    # Use resource_man register alias
    btn = QtWidgets.QPushButton(rsc.QIcon('edit-cut'), 'edit-cut', None)
    widg.layout().addWidget(btn)

    # Use Qt QResource alias name
    btn = QtWidgets.QPushButton(rsc.QIcon(':/edit-cut'), ':/edit-cut', None)
    widg.layout().addWidget(btn)

    # Use Qt QResource File name - DOES NOT WORK! CAN ONLY USE QRC ALIAS IDENTIFIER!
    # btn = QtWidgets.QPushButton(QIcon(':\\check_lib\\check_sub\\edit-cut.png'),
    #                                   'QFile name ":\\check_lib\\check_sub\\edit-cut.png"', None)
    # widg.layout().addWidget(btn)

    # Use resource_man register alias
    btn = QtWidgets.QPushButton(rsc.QIcon(":/check_lib/check_sub/document-new.png"), ":/check_lib/check_sub/document-new.png", None)
    widg.layout().addWidget(btn)

    # Use Qt QResource File name alias
    btn = QtWidgets.QPushButton(rsc.QIcon(":/rman2/check_lib/check_sub/document-new.png"), ":/rman2/check_lib/check_sub/document-new.png", None)
    widg.layout().addWidget(btn)


    flay = QtWidgets.QFormLayout()
    widg.layout().addLayout(flay)
    try:
        lbl = QtWidgets.QLabel()
        lbl.setPixmap(rsc.QPixmap(":/document-save-as").scaledToHeight(32))
        flay.addRow(":/document-save-as", lbl)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass
    try:
        lbl = QtWidgets.QLabel()
        lbl.setPixmap(rsc.QPixmap(":/rman2/document-save-as2").scaledToHeight(32))  # Must be compiled
        flay.addRow(":/rman2/document-save-as2", lbl)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass
    try:
        svg = rsc.QSvgWidget(":/document-save-as")
        svg.setFixedSize(32, 32)
        flay.addRow(":/document-save-as", svg)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass
    try:
        svg = rsc.QSvgWidget(":/rman2/document-save-as2")
        svg.setFixedSize(32, 32)
        flay.addRow(":/rman2/document-save-as2", svg)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass
    try:
        svg = rsc.QSvgWidget("document-save-as2")  # Check registered lookup using the linked manager
        svg.setFixedSize(32, 32)
        flay.addRow("document-save-as2", svg)
    except (rsc.ResourceNotAvailable, OSError, TypeError) as err:
        pass

    widg.show()
    app.exec_()
