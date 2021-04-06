import os

import pytest

from EZrename import get_files, renamed_files, rename
from EZrename.__main__ import get_predicates

DIR = ['dir1', 'dir2', 'dir3']
DOCX = ['docu.docx', 'docu2.docx']
TEXT = ['text.txt', 'text2.txt']
MKV = ['hello.mkv', 'hello2.mkv']
MP3 = ['hello3.mp3']
LIST_DIR = DIR + DOCX + TEXT + MKV + MP3

@pytest.fixture()
def testdir1(tmp_path):
    d = tmp_path / 'testdir1'
    d.mkdir()
    for element in LIST_DIR:
        if '.' in element:
            (d / element).touch()
        else:
            (d / element).mkdir()
  
    return d


get_files_parameters = [
    (None, LIST_DIR),
    (get_predicates(only=['mkv']), MKV),
    (get_predicates(only=['mkv', 'mp3']), MKV + MP3),
    (get_predicates(ignore=['mkv', 'mp3', 'txt']), DIR + DOCX),
    (get_predicates(ignore=['mkv']), DIR + DOCX + TEXT + MP3),
    (get_predicates(directory=True), DIR),
    (get_predicates(directory=True, only=['docx', 'mp3']), DIR + DOCX + MP3),
    (get_predicates(directory=True, ignore=['txt', 'docx', 'txt']), MKV + MP3),
    (get_predicates(directory=True, ignore=[]), DOCX + TEXT + MKV + MP3)
]
@pytest.mark.parametrize('predicates, expected', get_files_parameters)
def test_get_files(testdir1, predicates, expected):
    """check get_files with multiple predicates."""
    output = sorted([entry.name for entry in get_files(testdir1, predicates=predicates)])
    assert output == sorted(expected)


renamed_files_parameters = [
    (r'\d+', 'LOL', [
        ('dir1', 'dirLOL'), ('dir2', 'dirLOL'), ('dir3', 'dirLOL'),
        ('hello.mkv', 'hello.mkv'), ('hello2.mkv', 'helloLOL.mkv'), ('hello3.mp3', 'helloLOL.mpLOL')
    ]),
    (r'\d+', '', [
        ('dir1', 'dir'), ('dir2', 'dir'), ('dir3', 'dir'), ('hello.mkv', 'hello.mkv'),
        ('hello2.mkv', 'hello.mkv'), ('hello3.mp3', 'hello.mp')
    ]),
]
@pytest.mark.parametrize('regex, replace_with, expected', renamed_files_parameters)
def test_renamed_files(testdir1, regex, replace_with, expected):
    files = [
        entry for entry in os.scandir(testdir1)
        # directory, mkv and mp3 files have all the variations we need
        if entry.name.endswith('.mkv') or entry.name.endswith('.mp3') or entry.is_dir()
    ]
    expected = sorted([(str(testdir1/original), str(testdir1/new_name)) for original, new_name in expected])
    output = sorted(list(renamed_files(path=testdir1, files=files, regex=regex, replace_with=replace_with)))

    assert output == expected


def test_rename(testdir1):
    predicates = [lambda e: e.is_dir() or e.name.endswith('.mkv') or e.name.endswith('.mp3')]
    source = renamed_files(testdir1, get_files(testdir1, predicates), r'\d+', '')
    output = rename(source)

    after_rename = {
        'dir1': 'dir',
        'dir2': 'dir (1)',
        'dir3': 'dir (2)',
        'hello.mkv': 'hello.mkv',
        'hello2.mkv': 'hello (3).mkv',
        'hello3.mp3': 'hello.mp',
    }
    expected = {str(testdir1/after): str(testdir1/before) for before, after in after_rename.items()}

    assert output == expected
