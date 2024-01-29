import os, sys

class DictToObject(object):
    def __init__(self, data=None):
        if data is None:
            raise ValueError("data must not be None")
        else:
            data = dict(data)

        for key, val in data.items():
            setattr(self, key, self.compute_attr_value(val))

    def compute_attr_value(self, value):
        if isinstance(value, list):
            return [self.compute_attr_value(x) for x in value]
        elif isinstance(value, dict):
            return DictToObject(value)
        else:
            return value
