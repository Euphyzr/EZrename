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

import sys
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
        self.presets = self.jsdata.get('presets', {})
        self.history = self.jsdata.get('last_changes', {})
        
    def _is_restricted(self, element: Optional[int] = None, willadd: Optional[int] = 0) -> bool:
        """Checks if the length of an element has reached it's provided limit."""
        if self.limit is None:
            return False
        element = element or len(self.presets)
        return element + willadd > self.limit

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

    def get_regex(self, errorer: Callable = sys.exit, **kwargs) -> str:
        """Based on the keyword arguments, return a regex.
        
        Kwargs
        ------
        regex : str
            If this is provided this will be used.
        preset_regex : str
            If this is provided, preset by this name will be searched.
        """
        default = self.jsdata['regex_default']
        preset_regex = kwargs.pop('preset_regex')
        provided_regex = kwargs.pop('regex')

        if provided_regex:
            regex = provided_regex
        elif preset_regex:
            try:
                regex = self.presets[preset_regex]
            except KeyError:
                errorer("No preset exists by that name.")
        elif default:
            regex = default
        else:
            errorer("No default regex is setted up. "
                    "Consider setting up one or provide a regex or a valid preset.")

        return regex

    def get_history(self, path, errorer: Callable = sys.exit) -> dict:
        """Returns rename history for the provided path."""
        try:
            history = self.history[path].items()
        except KeyError:
            errorer("No rename history for this directory.")

        return history
        