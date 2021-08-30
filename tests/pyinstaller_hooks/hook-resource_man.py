from PyInstaller import config
from pylibimp import import_module
from resource_man.pyinstaller import registered_datas


import_module(config.CONF['main_script'], reset_modules=True)
datas = registered_datas()
print(datas)
