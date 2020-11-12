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
from typing import Optional, Union, Iterator, Tuple

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

    def filter_files(self, predicates: Optional[Union[list, tuple]] = None) -> Iterator[str]:
        predicates = predicates or [lambda e: True]
        with os.scandir(self.path) as it:
            for entry in it:
                if all(p(entry) for p in predicates):
                    yield entry.name

    def renamed_names(self, files: str, regex: str, replacewith: str) -> Iterator[Tuple[str, str]]:
        """A generator that yields a tuple of original path and renamed path of the file."""
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
