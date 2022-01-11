import os


def test_find_datas():
    from resource_man.pyinstaller import find_datas

    datas = find_datas('check_lib')
    
    rsc = (os.path.abspath('test_lib/check_lib/rsc.txt'), 'check_lib')
    assert rsc in datas
    rsc2 = (os.path.abspath('test_lib/check_lib/check_sub/rsc2.txt'), os.path.normpath('check_lib/check_sub'))
    assert rsc2 in datas


def test_registered_datas():
    import check_lib.check_sub
    from resource_man.pyinstaller import register, registered_datas

    rsc = register('check_lib', 'rsc.txt', ...)
    rsc2 = register('check_lib.check_sub', 'rsc2.txt', 'rsc2.txt')

    datas = registered_datas(use_dest_dirs=False)

    assert (os.path.relpath(str(rsc.files())), rsc.package_path) in datas
    assert (os.path.relpath(str(rsc2.files())), rsc2.package_path) in datas


if __name__ == '__main__':
    test_find_datas()
    test_registered_datas()

    print('All tests passed successfully!')
