import os
import sys
import shutil
import time
import contextlib
try:
    from subprocess import run
except (ImportError, Exception):
    from subprocess import Popen

    def run(*args, check=False, **kwargs):
        proc = Popen(*args, **kwargs)
        proc.wait()
        if check and proc.returncode != 0:
            raise RuntimeError('The program failed to run properly')
        return proc


SHELL = {'shell': True, 'stdout': sys.stdout, 'stderr': sys.stderr,
         'check': True, }
os.chdir(os.path.dirname(__file__))


def check_installed(**kwargs):
    # pyinstaller-hooks pylibimp requirement
    try:
        import pylibimp
    except (ImportError, Exception):
        run(['python', '-m', 'pip', 'install', 'pylibimp'], **SHELL)

    # install sub package
    try:
        import check_lib.check_sub
    except (ImportError, Exception):
        run(['python', '-m', 'pip', 'install', '-e', './test_lib'], **SHELL)


@contextlib.contextmanager
def compile_qt_qrc(main_module, run_two_cmds=True, delete_compiled=True, use_import=False, **kwargs):
    if use_import:
        try:
            import resource_man.qt as rsc

            # Compile resources
            if run_two_cmds:
                print('Create .qrc')
                rsc.create_qrc(main_module=main_module)
                print('Compile .qrc')
                rsc.compile_qrc()
            else:
                print('Create and Compile .qrc')
                rsc.create_compiled(main_module=main_module)

            yield
        finally:
            if delete_compiled:
                time.sleep(1)
                try: os.remove('resource_man_compiled_resources.qrc')
                except: pass
                try: os.remove('resource_man_compiled_resources.py')
                except: pass
    else:
        try:
            # Compile resources
            if run_two_cmds:
                print('Create .qrc')
                run(['python', '-m', 'resource_man.qt', 'create', main_module], **SHELL)
                print('Compile .qrc')
                run(['python', '-m', 'resource_man.qt', 'compile'], **SHELL)
            else:
                print('Create and Compile .qrc')
                run(['python', '-m', 'resource_man.qt', 'run', main_module], **SHELL)

            yield
        finally:
            if delete_compiled:
                time.sleep(1)
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
        run(args, **SHELL)

        yield
    finally:
        if delete_build:
            time.sleep(1)
            try: shutil.rmtree('build')
            except: pass
            try: os.remove('{0}.spec'.format(main_name))
            except: pass


@contextlib.contextmanager
def cxfreeze_exe(main_module, **kwargs):
    main_name = os.path.splitext(main_module)[0]

    # Python 3.4
    if sys.version_info < (3, 5):
        args = ['python', 'freeze.py', 'build']
    else:
        args = ['cxfreeze', main_module, '--target-dir', 'dist/{0}'.format(main_name),
                '--excludes', 'tcl,ttk,tkinter', ]
                # This will stop importlib.resources from working. Unless you include data files in the zip
                # '--zip-include-packages', 'check_lib']

    print('Create Cx_Freeze Executable')
    run(args, **SHELL)

    yield


def run_exe(main_module, delete_dist=True, **kwargs):
    main_name = os.path.splitext(main_module)[0]

    try:
        print('Run Executable')
        run(['call', '.\\dist\\{0}\\{0}.exe'.format(main_name)], **SHELL)
    finally:
        if delete_dist:
            time.sleep(1)
            try: shutil.rmtree('./dist')
            except: pass


if __name__ == '__main__':
    MAIN_MODULE = 'readme_qt.py'
    # MAIN_MODULE = 'run_linked.py'
    check_installed()

    # with compile_qt_qrc(MAIN_MODULE, run_two_cmds=True, delete_compiled=False):
    #     pass

    with compile_qt_qrc(MAIN_MODULE, run_two_cmds=True, delete_compiled=True, use_import=True):
        with pyinstaller_exe(main_module=MAIN_MODULE, run_hook=True, delete_build=True):
            run_exe(main_module=MAIN_MODULE, delete_dist=True)

    with compile_qt_qrc(MAIN_MODULE, run_two_cmds=True, delete_compiled=True, use_import=True):
        with cxfreeze_exe(main_module=MAIN_MODULE):
            run_exe(main_module=MAIN_MODULE, delete_dist=True)

    print('All checks ran successfully!')
