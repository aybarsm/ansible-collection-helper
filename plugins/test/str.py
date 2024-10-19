from __future__ import annotations
from ..common.tools import Validate, Str

def valid_json_object(str):
    """
    Check if the given string is a valid JSON object string
    """
    return Str.isJson(str, 'object')

def valid_json_array(str):
    """
    Check if the given string is a valid JSON array string
    """
    return Str.isJson(str, 'array')

def valid_json(str):
    """
    Check if the given string is a valid JSON string
    """
    return Str.isJson(str)

def omitted(str):
    """
    Check if the given string has the '__omit_place_holder__' prefix

    Example Usage: "{{ string is omitted() }}"
    """
    return Validate.isString(str) and str.startswith('__omit_place_holder__')

class TestModule(object):
    def tests(self):
        return {
            'valid_json_object': valid_json_object,
            'valid_json_array': valid_json_array,
            'valid_json': valid_json,
            'omitted': omitted
        }