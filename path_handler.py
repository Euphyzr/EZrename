import os
import sys

class PathHandlerException(Exception):
    pass

class PathHandler:
    """Attributes:
    [object]
    invalid_turns[int]: Number of input turns for invalid path.
    same_turns[int]   : Number of input turns for destination path with same source.
    term_msg[str]     : Message on terminatting path input.
    noexist_msg[str]  : Promt after path not existing.
    samepath_msg[str] : Promt after source and destination path being same.
    sys_exit[bool]    : exit programme after terminating input.
    """

    def __init__(self, **kwargs):
        # Set the default values 
        self.invalid_turns = kwargs.get('invalid_turns', 1)
        self.same_turns = kwargs.get('same_turns', 1)
        self.term_msg = kwargs.get('term_msg', "Cancelled")
        self.noexist_msg = kwargs.get('noexist_msg', "Path doesn't exist. Re-enter: ")
        self.samepath_msg = kwargs.get('samepath_msg', "Source and destination can't be same. Re-enter: ")
        self.sys_exit = kwargs.get('sys_exit', False)

    def input_validator(self, path):
        """Returns a valid path after checking. If the path's not valid then invalid_turns-1 times."""
        for turn in range(self.invalid_turns):
            if os.path.isdir(path):
                return path
            
            elif path == "":
                print(self.term_msg)
                if self.sys_exit:
                    sys.exit()
                break

            elif not os.path.isdir(path):
                if turn == self.invalid_turns-1:
                    print(self.term_msg)
                    if self.sys_exit:
                        sys.exit()
                    break
                else:
                    path = input(self.noexist_msg)
    
    def samepath_validator(self, src, dst):
        """Returns path after checking source and destination path are different. If same then asks
        for valid input [input_validator()] same_turn-1 times."""
        for turn in range(self.same_turns):
            if src != dst:
                return dst
            
            elif src == dst:
                if turn == self.same_turns-1:
                    print(self.term_msg)
                    if self.sys_exit:
                        sys.exit()
                    break
                else:
                    dst = self.input_validator(input(self.samepath_msg))
    
    def configure(self, show_change=False, **kwargs):
        """Change the value of any attribute of the object. Extra Parameter: show_change=False"""
        for k, v in kwargs.items():
            if hasattr(self, k):        # To avoid adding unnecessary attributes
                old_v = getattr(self, k)
                setattr(self, k, v)
                if show_change:
                    print(f"{k}: {old_v} ---> {v}")
