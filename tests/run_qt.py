import check_lib.check_sub  # Must import packages with subpackages that use importlib.resources
from qtpy import QtWidgets
from resource_man.qt import QIcon, register, get_binary, read_binary


# Register package resources to an identifier that can be used with fromTheme
# must import check_lib.check_sub for importlib.resources to work
register('edit-cut', 'check_lib.check_sub', 'edit-cut.png')


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
    btn_binary_importlib = QtWidgets.QPushButton(QIcon(read_binary('check_lib.check_sub', 'edit-cut.png')), 'importlib resource_man')
    widg.layout().addWidget(btn_binary_importlib)

    app.exec_()
