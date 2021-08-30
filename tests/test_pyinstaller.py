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

    rsc = register('rsc.txt', 'check_lib', 'rsc.txt')
    rsc2 = register('rsc2.txt', 'check_lib.check_sub', 'rsc2.txt')

    datas = registered_datas()

    assert (os.path.relpath(str(rsc.files())), os.path.dirname(rsc.get_package_path())) in datas
    assert (os.path.relpath(str(rsc2.files())), os.path.dirname(rsc2.get_package_path())) in datas


if __name__ == '__main__':
    test_find_datas()
    test_registered_datas()

    print('All tests passed successfully!')
