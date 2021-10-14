"""Old CX Freeze like seutp.py"""
import os
import sys
import shutil
from cx_Freeze import setup, Executable

main_module = 'readme_qt.py'
main_name = os.path.splitext(main_module)[0]
target_dir = 'dist/' + main_name

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["os", 're', 'atexit'], "excludes": ['tcl', 'ttk',"tkinter"]}
include_files = build_exe_options['include_files'] = []

try:
    import resource_man
    __import__(main_name)  # Import main to register resources

    for src, dest in resource_man.registered_datas():
        basename = os.path.basename(src)
        if not dest.endswith(basename):
            dest = os.path.join(dest, basename)
        include_files.append((src, dest))
except (ImportError, Exception):
    pass

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(main_module, base=base)
    ]

setup(
    name=main_name,
    version="0.1",
    description="My GUI application!",
    options={"build_exe": build_exe_options},
    executables=executables,
    )

# Move to dist dirs
print('Moving to dist')
os.makedirs('dist', exist_ok=True)
for exe in executables:
    target = getattr(exe, 'targetName', '')
    dest = 'dist/' + main_name
    if target and os.path.exists(target):
        try:
            shutil.rmtree(dest)
        except:
            pass
        os.rename(os.path.dirname(target), dest)
        try:
            shutil.rmtree('build')
        except:
            pass
