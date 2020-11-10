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
