import os
import sys
import shutil
import subprocess
import contextlib


SHELL = {'shell': True, 'stdout': sys.stdout, 'stderr': sys.stderr}
os.chdir(os.path.dirname(__file__))


def check_installed(**kwargs):
    # pyinstaller-hooks pylibimp requirement
    try:
        import pylibimp
    except (ImportError, Exception):
        assert subprocess.run(['python', '-m', 'pip', 'install', 'pylibimp'], **SHELL).returncode == 0

    # install sub package
    try:
        import check_lib.check_sub
    except (ImportError, Exception):
        assert subprocess.run(['python', '-m', 'pip', 'install', './test_lib'], **SHELL).returncode == 0


@contextlib.contextmanager
def compile_qt_qrc(main_module, run_two_cmds=True, delete_compiled=True, **kwargs):
    try:
        # Compile resources
        if run_two_cmds:
            print('Create .qrc')
            assert subprocess.run(['python', '-m', 'resource_man.qt', 'create', main_module], **SHELL).returncode == 0
            print('Compile .qrc')
            assert subprocess.run(['python', '-m', 'resource_man.qt', 'compile'], **SHELL).returncode == 0
        else:
            print('Create and Compile .qrc')
            assert subprocess.run(['python', '-m', 'resource_man.qt', 'run', main_module], **SHELL).returncode == 0

        yield
    finally:
        if delete_compiled:
            try: os.remove('resource_man_compiled_resources.qrc')
            except: pass
            try: os.remove('resource_man_compiled_resources.py')
            except: pass


@contextlib.contextmanager
def pyinstaller_exe(main_module, run_hook=True, delete_build=True, **kwargs):
    main_name = os.path.splitext(main_module)[0]

    # Make executable with pyinstaller
    args = ['pyinstaller', main_module, '-y']
    if run_hook:
        args.extend(['--additional-hooks-dir', 'pyinstaller_hooks'])
    else:
        # --add-data Required for importlib.resources read_binary
        args.extend(['--add-data', 'test_lib/check_lib/rsc.txt;check_lib'])
        args.extend(['--add-data', 'test_lib/check_lib/check_sub/rsc2.txt;check_lib/check_sub'])
        args.extend(['--add-data', 'test_lib/check_lib/check_sub/edit-cut.png;check_lib/check_sub'])
        args.extend(['--add-data', 'test_lib/check_lib/check_sub/document-new.png;check_lib/check_sub'])

    try:
        print('Create PyInstaller Executable')
        assert subprocess.run(args, **SHELL).returncode == 0

        yield
    finally:
        if delete_build:
            try: shutil.rmtree('build')
            except: pass
            try: os.remove('{0}.spec'.format(main_name))
            except: pass


@contextlib.contextmanager
def cxfreeze_exe(main_module, **kwargs):
    main_name = os.path.splitext(main_module)[0]

    args = ['cxfreeze', main_module, '--target-dir', 'dist/{0}'.format(main_name),
            '--excludes', 'tcl,ttk,tkinter', ]
            # This will stop importlib.resources from working. Unless you include data files in the zip
            # '--zip-include-packages', 'check_lib']

    print('Create Cx_Freeze Executable')
    assert subprocess.run(args, **SHELL).returncode == 0

    yield


def run_exe(main_module, delete_dist=True, **kwargs):
    main_name = os.path.splitext(main_module)[0]

    try:
        print('Run Executable')
        assert subprocess.run(['call', '.\\dist\\{0}\\{0}.exe'.format(main_name)], **SHELL).returncode == 0
    finally:
        if delete_dist:
            try: shutil.rmtree('dist')
            except: pass


if __name__ == '__main__':
    MAIN_MODULE = 'readme_qt.py'
    check_installed()

    with compile_qt_qrc(MAIN_MODULE, run_two_cmds=True, delete_compiled=True):
        with pyinstaller_exe(main_module=MAIN_MODULE, run_hook=True, delete_build=True):
            run_exe(main_module=MAIN_MODULE)

    with compile_qt_qrc(MAIN_MODULE, run_two_cmds=True, delete_compiled=True):
        with cxfreeze_exe(main_module=MAIN_MODULE):
            run_exe(main_module=MAIN_MODULE)

    print('All checks ran successfully!')
