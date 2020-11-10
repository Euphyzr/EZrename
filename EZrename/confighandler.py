import json
from typing import Optional, Callable

class ConfigHandler:
    """A class to handle EZrename configuration.
    
    Attributes
    ----------
    jsonfile : str
        The path to configuration json file. 
    indent : int, optional
        Indent when dumping json.
    limit : int, optional
        Maximum number of presets.
    jsdata : dict
        The entire json data.
    redefault : str, optional
        The default regex pattern.
    presets : dict, optional
        The presets dictionary
    """

    def __init__(self, jsonfile, **kwargs):
        self.indent = kwargs.pop('indent', 4)
        self.limit = kwargs.pop('limit', None)
        self.jsonfile = jsonfile
        self._callbacks = []  # they're called on restriction

        with open(jsonfile, 'r') as jfp:
            self.jsdata = json.load(jfp)
        self.redefault = self.jsdata.get('regex_default', None)
        self.presets = self.jsdata.get('presets', {})
        
    def _is_restricted(self, element: Optional[int] = None, willadd: Optional[int] = 0) -> bool:
        """Checks if the length of an element has reached it's provided limit."""
        if self.limit is None:
            return False
        element = element or len(self.presets)
        return element + willadd >= self.limit

    def on_restriction(self, callback: Callable) -> None:
        """Bind a callable to be called on length restriction of an element."""
        self._callbacks.append(callback)

    def presupdate(self, new: dict) -> None:
        """Updates preset after checking limit."""
        if self._is_restricted(len(self.presets), len(new)):
            if self._callbacks:
                for callback in self._callbacks:
                    callback()
                return
            raise ValueError(f"Maximum number of preset is {self.limit}.")
        self.presets.update(new)
    
    def dump(self, **kwargs) -> None:
        """Dump the datas to the json file."""
        with open(self.jsonfile, 'w') as jfp:
            json.dump(self.jsdata, jfp, indent=self.indent, **kwargs)
