"""
MIT License

Copyright (c) 2020-2021 Euphyzr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import re

def get_files(path, predicates=None):
    """Filters and yields os.DirEntry according to provided predicates, after yielding the path."""
    with os.scandir(path) as it:
        for entry in it:
            if predicates:
                if all(p(entry) for p in predicates):
                    yield entry
            else:
                yield entry

def renamed_files(path, files, regex, replace_with):
    """Yields full path of original and renamed name of files, based on regex and replace_with."""
    pattern  = re.compile(regex)
    for entry in files:
        # we only want to change the file name not the whole path, so use os.path.join
        new_name = os.path.join(path, pattern.sub(replace_with, entry.name))
        original = entry.path
        yield original, new_name

def rename(
    source,
    on_rename=lambda original, new_name: print(original, '->', new_name),
    on_permission_error=lambda err: print(f"{err}\nSkipping...\n")
):
    """Renames based on source, which is an sequence of tuple of original and to be renamed path. Return
    a dictionary of (new_name: old_name) key, value pair.

    source : Sequence[Tuple[str, str]]
        Rename all files in the source from their original name to new_name
    on_rename : function [Optional]
        A function to be called after each rename. Takes original and to-be renamed path as an input.
    on_permission_error : function [Optional]
        A function to be called on PermissionError. Takes error as the input.
    """
    same_name_count = 1
    history = {}

    for original, new_name in source:
        try:
            os.rename(original, new_name)
        except PermissionError as perm_err:
            on_permission_error(perm_err)
            continue
        except FileExistsError:
            name, ext = os.path.splitext(new_name)
            new_name = f'{name} ({same_name_count}){ext}'
            os.rename(original, new_name)
            same_name_count += 1

        history[new_name] = original
        on_rename(original, new_name)

    return history
