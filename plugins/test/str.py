from __future__ import annotations
from ..common.tools import Str

def valid_json_object(data):
    """
    Check if the given data is a valid JSON object string
    """
    return Str.isJson(data, 'object')

def valid_json_array(data):
    """
    Check if the given data is a valid JSON array string
    """
    return Str.isJson(data, 'array')

def valid_json(data):
    """
    Check if the given data is a valid JSON string
    """
    return Str.isJson(data)

class TestModule(object):
    def tests(self):
        return {
            'valid_json_object': valid_json_object,
            'valid_json_array': valid_json_array,
            'valid_json': valid_json,
        }