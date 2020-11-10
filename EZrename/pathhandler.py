import os
import sys
from typing import Optional

class PathHandler:
    """A class to handle path inputs.
    
    Attributes
    ----------
    invalids : int, optional
        The number of times, user will be promted because of an invalid path
    sames : int, optional. 
        The number of times user will be promted because of a destination path
        which is the same as the source path.
    on_termination : str, optional
        The message to show when the input session is terminated.
    on_nonexistence : str, optional
        The message to promt the user with, incase the path is invalid.
    on_samepath : str, optional
        The message to promt the user with, incase the destination is the same as
        the source path.
    sys_exit : bool, optional
        If the programme should sys.exit() or not, on termination. False by default. 
    """

    def __init__(self, **kwargs):
        self.invalids = kwargs.get('invalids', 0)
        self.sames = kwargs.get('sames', 0)
        self.on_termination = kwargs.get('on_termination', "Cancelled.")
        self.on_nonexistence = kwargs.get('on_nonexistence', "Path doesn't exist. Re-enter: ")
        self.on_samepath = kwargs.get('on_samepath', "Source and destination can't be same. Re-enter: ")
        self.sys_exit = kwargs.get('sys_exit', False)

    def input_validate(self, path: str) -> Optional[str]:
        """Returns a path after checking if it exists."""
        for turn in range(self.invalids + 1):
            # the (+ 1) in range and break if turn == self.invalids 
            # is because we don't want to terminate if the user gives
            # a valid input in the last turn
            if os.path.isdir(path):
                return path
            if path == "" or turn == self.invalids:
                break
            path = input(self.on_nonexistence)
        print(self.on_termination)
        if self.sys_exit:
            sys.exit()

    def samepath_validate(self, src: str, dst: str) -> Optional[str]:
        """Returns destination path if it's not same as src."""
        for turn in range(self.sames + 1):
            try:
                if src != dst and os.path.isdir(dst):
                    return dst
            except TypeError:
                # Empty input to cancel same path validation
                break
            if turn == self.sames:
                # Will show termination message only after the 'last' turn
                # Otherwise, termination caused by empty input is dealt with
                # in input validator method
                print(self.on_termination)
                break
            dst = self.input_validate(input(self.on_samepath))
        if self.sys_exit:
            sys.exit()
