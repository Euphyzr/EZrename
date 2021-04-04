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

class ConfigHandler:
    """A helper class for EZrename command-line tool configuration.
    
    Attributes
    ----------
    jsonfile : str
        The path to configuration json file. 
    indent : int, optional
        Indent when dumping json.
    errorer : function, option
        Function called for errors. sys.exit by default.
    limit : int, optional
        Maximum number of presets.
    jsdata : dict, attribute
        The entire json data.
    presets : dict, attribute
        The presets dictionary
    """

    def __init__(self, jsonfile, **kwargs):
        self.indent = kwargs.pop('indent', 4)
        self.limit = kwargs.pop('limit', None)
        self.jsonfile = jsonfile
        self.errorer = kwargs.pop('errorer', sys.exit)
        self.restriction_msg = kwargs.get('restriction_msg', f"Max {self.limit} presets allowed.")

        with open(jsonfile, 'r') as jfp:
            self.jsdata = json.load(jfp)
        self.presets = self.jsdata.get('presets', {})
        self.history = self.jsdata.get('last_changes', {})

    def update_preset(self, new):
        if self.limit and (len(self.presets) + len(new) > self.limit):
            self.errorer(self.restriction_msg)
            return
        self.presets.update(new)

    def dump(self, **kwargs):
        """Dump the datas to the json file."""
        with open(self.jsonfile, 'w') as jfp:
            json.dump(self.jsdata, jfp, indent=self.indent, **kwargs)

    
    def get_regex(self, regex=None, preset_regex=None):
        """Based on the keyword arguments, return a regex.
        
        Kwargs
        ------
        regex : str
            If this is provided this will be used.
        preset_regex : str
            If this is provided, preset by this name will be searched.
        """
        default = self.jsdata['regex_default']

        if regex:
            result = regex
        elif preset_regex:
            try:
                result = self.presets[preset_regex]
            except KeyError:
                self.errorer("No preset exists by that name.")
        elif default:
            result = default
        else:
            self.errorer(
                "No default regex is setted up. Consider setting up one or provide a regex or a valid preset."
            )

        return result
    
    def get_history(self, path):
        """Returns rename history for the provided path."""
        try:
            history = self.history[path].items()
        except KeyError as e:
            self.errorer(f"No rename history for {e}.")

        return history
