import json

class JsonConfigHandler:
    """Pass a valid path/to/json file
    """
    def __init__(self, jsonfile):
        self.jsonfile = jsonfile
        self.restriction_callbacks = []

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
        is equal or more than the imposed restriction. Callbacks must have **kwargs argument"""
        self.restriction_callbacks.append(callback)

    def append_to_object_element(self, element, key, val, length_restriction=False, **kwargs):
        """Updates the target json object with provided key and value. In case of length_restriction,
        length's value must be provided (e.g length=5)"""
        if length_restriction:
            if self.is_restricted_by_length(element, kwargs['length']):
                for fn in self.restriction_callbacks:
                    fn(**kwargs)
            else:
                self.json_data[element][key] = val
        else:
            self.json_data[element][key] = val

    def append_to_array_element(self, element, val, length_restriction=False, **kwargs):
        """Updates the target json array with provided value. In case of length_restriction,
        length's value must be provided (e.g length=5)"""
        if length_restriction:
            if self.is_restricted_by_length(element, kwargs['length']):
                for fn in self.restriction_callbacks:
                    fn(**kwargs)
            else:
                self.json_data[element] + val
        else:
            self.json_data[element] + val
    
    def dump(self, **kwargs):
        """Calls json.dumb() with the (modified) data and provided json file. **kwargs for
        additional json.dump() arguments"""
        with open(self.jsonfile, "w") as fp:
            json.dump(self.json_data, fp, **kwargs)
