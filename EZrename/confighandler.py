import json

class ConfigHandler:
    def __init__(self, jsonfile, **kwargs):
        self.indent = kwargs.pop('indent', 4)
        self.limit = kwargs.pop('limit', None)
        self.jsonfile = jsonfile
        self.callbacks = []  # they're called on restriction

        with open(jsonfile, 'r') as jfp:
            self._jsdata = json.load(jfp)
        self.redefault = self._jsdata.get('regex_default', None)
        self.presets = self._jsdata.get('presets', {})
        
    def _is_restricted(self, element=None, willadd=0) -> bool:
        """Checks if the length of an element has reached it's provided limit."""
        if self.limit is None:
            return False
        element = element or len(self.presets)
        return element + willadd >= self.limit

    def on_restriction(self, callback) -> None:
        """Bind a callable to be called on length restriction of an element."""
        self.callbacks.append(callback)

    def presupdate(self, new: dict) -> None:
        """Updates preset after checking limit."""
        if self._is_restricted(len(self.presets), len(new)):
            if self.callbacks:
                for callback in self.callbacks:
                    callback()
                return
            raise ValueError("Maximum number of preset is {0}.".format(self.limit))
        self.presets.update(new)
    
    def dump(self, **kwargs) -> None:
        """Dump the datas to the json file."""
        with open(self.jsonfile, 'w') as jfp:
            json.dump(self._jsdata, jfp, indent=self.indent, **kwargs)
