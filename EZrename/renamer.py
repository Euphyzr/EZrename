"""
MIT License

Copyright (c) 2020 Euphyzr

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
from typing import Optional, Union, Iterator, Tuple, Sequence

class EzRenamer:
    """A class that handles filtering and renaming the files.

    Attributes
    ----------
    path : str
        Path of the target directory.
    phandler : PathHandler
        A path handler object.
    """

    def __init__(self, path, phandler):
        self.phandler = phandler
        self.path = self.phandler.input_validate(path)
        self._predicates = [lambda e: True]

    def add_predicates(self, **kwargs) -> None:
        """Add predicates to filter the files with.
        
        Kwargs
        ------
        ignore : Sequence
            Ignores file extension in this sequence.
        only : Sequence
            Only accepts file extensions in this sequence.
        directoy : bool
            Calling with ignore, ignores the extensions and directories. If no extension
            is provided then only ignore directories. Calling with only filters only directories
            and those extensions.
        """

        get_ext = lambda en: os.path.splitext(en)[1][1:]
        predicates = []

        only = kwargs.pop('only')
        ignore = kwargs.pop('ignore')
        directory = kwargs.pop('directory')

        if directory:
            if only:
                # --directory with --only includes directories
                predicates.append(lambda e: e.is_dir() or get_ext(e.name) in only)
            elif ignore:
                # --directory with --ignore ignores directories
                predicates.append(lambda e: not e.is_dir() and not get_ext(e.name) in ignore)
            elif not ignore and type(ignore) == list:
                # calling -i without any args gives an empty list use this behaviour to ignore directories
                predicates.append(lambda e: not e.is_dir())
            else:
                predicates.append(lambda e: e.is_dir())
        else:
            if ignore:
                predicates.append(lambda e: not get_ext(e.name) in ignore)
            if only:
                predicates.append(lambda e: get_ext(e.name) in only)

        self._predicates = predicates if predicates else self._predicates

    def filter_files(self, predicates: Optional[Union[list, tuple]] = None) -> Iterator[str]:
        if predicates is None:
            predicates = self._predicates

        with os.scandir(self.path) as it:
            for entry in it:
                if all(p(entry) for p in predicates):
                    yield entry.name

    def renamed_names(self, regex: str, replacewith: str, files: Iterator[str] = None) -> Iterator[Tuple[str, str]]:
        """A generator that yields a tuple of original path and renamed path of the file."""
        if files is None:
            files = self.filter_files()
        for originalnames in files:
            renamed = os.path.join(self.path, re.sub(regex, replacewith, originalnames))
            originalnames = os.path.join(self.path, originalnames)
            yield originalnames, renamed

    def rename(self, source: Tuple[str, str], undo: bool = False, quiet: bool = False) -> dict:
        """Renames and returns a dictionary with original, renamed pairs."""
        exception_count, history = 1, {}

        for original, renamed in source:
            original, renamed = (renamed, original) if undo else (original, renamed)
            try:
                os.rename(original, renamed)
            except FileExistsError:
                renamed = f"{renamed} ({exception_count})"
                os.rename(original, renamed)
                exception_count += 1
            if not quiet:
                print(original, '------>', renamed)
            history[original] = renamed

        return history
