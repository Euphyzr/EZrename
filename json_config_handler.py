import json

class JsonConfigHandler:
    """Pass a valid path/to/json file
    """
    def __init__(self, jsonfile, json_indent=None):
        self.jsonfile = jsonfile
        self.restriction_callbacks = []
        self.json_indent = json_indent

        with open(jsonfile, "r") as fp:
            self.json_data = json.load(fp)
    
    def is_restricted_by_length(self, element, length):
        """Checks if length of an element is yet restricted"""
        if len(self.json_data[element]) >= length:
            return True
        else:
            return False

    def on_restriction(self, callback):
        """Allows to bind a callable that will be called when length of target json element 
        is equal or more than the imposed restriction."""
        self.restriction_callbacks.append(callback)

    def append_to_object_element(self, element, key, val, length):
        """Updates the target json object with provided key and value. In case of reaching length restriction,
        restriction callbacks will be called"""
        if self.is_restricted_by_length(element, length):
                for fn in self.restriction_callbacks:
                    fn()
        else:
            self.json_data[element][key] = val

    def dump(self, **kwargs):
        """Calls json.dumb() with the (modified) data and provided json file. **kwargs for
        additional json.dump() arguments"""
        with open(self.jsonfile, "w") as fp:
            json.dump(self.json_data, fp, indent=self.json_indent, **kwargs)