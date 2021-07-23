import os
import shutil
import subprocess


def run_pyinstaller():
    os.chdir(os.path.dirname(__file__))

    cp = subprocess.run('pyinstaller run_qt.py --noconfirm --additional-hooks-dir pyinstaller_hooks')
    try: shutil.rmtree('build')
    except: pass
    try: os.remove('run_qt.spec')
    except: pass
    assert cp.returncode == 0

    cp = subprocess.run('dist/run_qt/run_qt.exe')
    try: shutil.rmtree('dist')
    except: pass
    assert cp.returncode == 0


def run_cxfreeze():
    os.chdir(os.path.dirname(__file__))

    cp = subprocess.run('cxfreeze run_qt.py --target-dir distcx/run_qt --excludes "tcl,ttk,tkinter"')
    assert cp.returncode == 0

    cp = subprocess.run('distcx/run_qt/run_qt.exe')
    try: shutil.rmtree('distcx')
    except: pass
    assert cp.returncode == 0


if __name__ == '__main__':
    run_pyinstaller()
    run_cxfreeze()

    print('All checks ran successfully!')
