

def test_files():
    from resource_man import files, rsc_files

    binary = files('check_lib').joinpath('rsc.txt').read_bytes()
    expected = b'rsc.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary

    binary = files('check_lib.check_sub').joinpath('rsc2.txt').read_bytes()
    expected = b'rsc2.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary

    # This library
    binary = rsc_files('check_lib').joinpath('rsc.txt').read_bytes()
    expected = b'rsc.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary

    binary = rsc_files('check_lib.check_sub').joinpath('rsc2.txt').read_bytes()
    expected = b'rsc2.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary


def test_as_file():
    from pathlib import Path
    from resource_man import files, as_file, rsc_files, rsc_as_file

    with as_file(files('check_lib').joinpath('rsc.txt')) as filename:
        assert Path(filename) == Path('test_lib/check_lib/rsc.txt').absolute(), Path(filename)

    with as_file(files('check_lib.check_sub').joinpath('rsc2.txt')) as filename:
        assert Path(filename) == Path('test_lib/check_lib/check_sub/rsc2.txt').absolute(), Path(filename)

    # This library
    with rsc_as_file(rsc_files('check_lib').joinpath('rsc.txt')) as filename:
        assert Path(filename) == Path('test_lib/check_lib/rsc.txt').absolute(), Path(filename)

    with rsc_as_file(rsc_files('check_lib.check_sub').joinpath('rsc2.txt')) as filename:
        assert Path(filename) == Path('test_lib/check_lib/check_sub/rsc2.txt').absolute(), Path(filename)


def test_read_text():
    from resource_man import read_text, rsc_read_text

    txt = read_text('check_lib', 'rsc.txt')
    expected = 'rsc.txt'
    assert txt == (expected + '\n') or txt == (expected + '\r\n'), txt

    txt = read_text('check_lib.check_sub', 'rsc2.txt')
    expected = 'rsc2.txt'
    assert txt == (expected + '\n') or txt == (expected + '\r\n'), txt

    # This library
    txt = rsc_read_text('check_lib', 'rsc.txt')
    expected = 'rsc.txt'
    assert txt == (expected + '\n') or txt == (expected + '\r\n'), txt

    txt = rsc_read_text('check_lib.check_sub', 'rsc2.txt')
    expected = 'rsc2.txt'
    assert txt == (expected + '\n') or txt == (expected + '\r\n'), txt


def test_read_binary():
    from resource_man import read_binary, rsc_read_binary

    binary = read_binary('check_lib', 'rsc.txt')
    expected = b'rsc.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary

    binary = read_binary('check_lib.check_sub', 'rsc2.txt')
    expected = b'rsc2.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary

    # This Library
    binary = rsc_read_binary('check_lib', 'rsc.txt')
    expected = b'rsc.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary

    binary = rsc_read_binary('check_lib.check_sub', 'rsc2.txt')
    expected = b'rsc2.txt'
    assert binary == (expected + b'\n') or binary == (expected + b'\r\n'), binary


def test_contents():
    from resource_man import contents, rsc_contents

    cont = list(contents('check_lib'))  # contents returns a list_iterator
    assert all(name in cont for name in ['__init__.py', 'rsc.txt']), cont

    cont = list(contents('check_lib.check_sub'))
    assert all(name in cont for name in ['__init__.py', 'rsc2.txt', 'edit-cut.png']), cont

    # This Library
    cont = list(rsc_contents('check_lib'))  # contents returns a list_iterator
    assert all(name in cont for name in ['__init__.py', 'rsc.txt']), cont

    cont = list(rsc_contents('check_lib.check_sub'))
    assert all(name in cont for name in ['__init__.py', 'rsc2.txt', 'edit-cut.png']), cont


def test_is_resource():
    from resource_man import is_resource, rsc_is_resource

    assert is_resource('check_lib', 'rsc.txt')
    assert is_resource('check_lib.check_sub', 'rsc2.txt')

    # This Library
    assert rsc_is_resource('check_lib', 'rsc.txt')
    assert rsc_is_resource('check_lib.check_sub', 'rsc2.txt')


def test_register():
    import resource_man as rsc

    rsc.clear()

    RSC = rsc.register('check_lib', 'rsc.txt', ...)  # QFile ":/rsc.txt"
    RSC2 = rsc.register('check_lib.check_sub', 'rsc2.txt', ...)  # QFile ":/rsc2.txt"
    EDIT_CUT = rsc.register('check_lib.check_sub', 'edit-cut.png', alias='edit-cut')  # QFile ":/edit-cut"
    DOC_NEW = rsc.register('check_lib.check_sub', 'document-new.png')  # QFile ":/check_lib/check_sub/document-new.png"

    assert RSC in rsc.get_global_manager()
    assert RSC2 in rsc.get_global_manager()
    assert EDIT_CUT in rsc.get_global_manager()
    assert DOC_NEW in rsc.get_global_manager()

    assert rsc.has_resource(RSC)
    assert rsc.has_resource(RSC2)
    assert rsc.has_resource(EDIT_CUT)
    assert rsc.has_resource(DOC_NEW)

    assert rsc.has_resource('rsc.txt')
    assert rsc.has_resource('check_lib', 'rsc.txt')
    assert rsc.has_resource('rsc2.txt')
    assert rsc.has_resource('check_lib.check_sub', 'rsc2.txt')
    assert rsc.has_resource('edit-cut')
    assert rsc.has_resource('check_lib.check_sub', 'edit-cut.png')
    assert rsc.has_resource('check_lib/check_sub/document-new.png')
    assert rsc.has_resource('check_lib.check_sub', 'document-new.png')

    # Unregister by alias
    rsc.unregister('edit-cut')
    assert not rsc.has_resource('edit-cut')
    rsc.register('check_lib.check_sub', 'edit-cut.png', alias='edit-cut')
    assert rsc.has_resource('edit-cut')
    rsc.unregister(alias='edit-cut')
    assert not rsc.has_resource('edit-cut')

    # Unregister by package, name
    rsc.unregister('check_lib.check_sub', 'rsc2.txt')
    assert not rsc.has_resource('check_lib.check_sub', 'rsc2.txt')

    # Unregister package_path
    rsc.unregister('check_lib/check_sub/document-new.png')
    assert not rsc.has_resource('check_lib/check_sub/document-new.png')

    # Unregister Resource object
    rsc.unregister(RSC)
    assert not rsc.has_resource('check_lib', 'rsc.txt')


def test_register_directory():
    import resource_man as rsc

    directory = rsc.register_directory('check_lib.check_sub', extensions=['.txt', '.png'])

    assert len(directory) > 0
    assert isinstance(directory[0], rsc.Resource)
    assert 'check_lib/check_sub/edit-cut.png' in directory
    assert 'check_lib/check_sub/document-new.png' in directory
    assert 'check_lib/check_sub/rsc2.txt' in directory

    directory = rsc.register_directory('check_lib', 'check_directory1', extensions=['.txt', '.png'])
    assert len(directory) == 1
    assert isinstance(directory[0], rsc.Resource)
    assert 'check_lib/check_directory1/edit-cut.png' in directory

    directory = rsc.register_directory('check_lib', 'check_directory1/check_directory2', extensions=['.txt', '.png'])
    assert len(directory) == 1
    assert isinstance(directory[0], rsc.Resource)
    assert 'check_lib/check_directory1/check_directory2/edit-cut.png' in directory

    directory = rsc.register_directory('check_lib', 'check_directory1', recursive=True,
                                       # exclude from given directory "check_directory1".
                                       exclude=['edit-cut.png'],  # ["check_directory2/edit-cut.png"] for other file
                                       extensions=['.txt', '.png'])
    assert len(directory) == 1
    assert isinstance(directory[0], rsc.Resource)
    assert 'check_lib/check_directory1/check_directory2/edit-cut.png' in directory
    assert 'check_lib/check_directory1/edit-cut.png' not in directory



if __name__ == '__main__':
    test_files()
    test_as_file()
    test_read_text()
    test_read_binary()
    test_contents()
    test_is_resource()
    test_register()
    test_register_directory()

    print('All tests passed successfully!')
