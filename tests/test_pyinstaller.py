import os


def test_collect_datas():
    from resource_man.pyinstaller import collect_datas

    datas = collect_datas('check_lib')
    
    rsc = (os.path.abspath('check_lib/rsc.txt'), 'check_lib')
    assert rsc in datas
    rsc2 = (os.path.abspath('check_lib/check_sub/rsc2.txt'), os.path.normpath('check_lib/check_sub'))
    assert rsc2 in datas


if __name__ == '__main__':
    test_collect_datas()

    print('All tests passed successfully!')
