from __future__ import annotations
from ..common.tools import Validate

def contains_all(data, items):
    """
    Check if the given list has all the given items

    Example Usage: "{{ data | contains_all(['item1', 'item2']) }}"
    """
    Validate.list(data, 'data')
    Validate.list(items, 'items')

    return len(list(set(data) & set(items))) == len(items)

def contains_any(data, items):
    """
    Check if the given list has any of the given items

    Example Usage: "{{ data | contains_any(['item1', 'item2']) }}"
    """
    Validate.list(data, 'data')
    Validate.list(items, 'items')

    return len(list(set(data) & set(items))) > 0

def has_all_keys(data, keys):
    """
    Check if the given dictionary has all the given keys

    Example Usage: "{{ data | has_keys(['key1', 'key2']) }}"
    """
    Validate.dict(data, 'data')
    Validate.list(keys, 'keys')

    return len(list(set(data.keys()) & set(keys))) == len(keys)

def has_any_keys(data, keys):
    """
    Check if the given dictionary has any of the given keys

    Example Usage: "{{ data | has_keys(['key1', 'key2']) }}"
    """
    Validate.dict(data, 'data')
    Validate.list(keys, 'keys')

    return len(list(set(data.keys()) & set(keys))) > 0

class TestModule(object):
    def tests(self):
        return {
            'contains_all': contains_all,
            'contains_any': contains_any,
            'has_all_keys': has_all_keys,
            'has_any_keys': has_any_keys
        }