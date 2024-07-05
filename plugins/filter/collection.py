from __future__ import annotations
from ansible.errors import AnsibleFilterError
from ..common.tools import Validate, Dict

def only_with(data, attributes):
    """
    Return a dictionary or list of dictionaries 
    with only the keys that are in the provided list.

    Example Usage: "{{ data | only_with(['key1', 'key2']) }}"

    Option Parameters:
     - attributes: The list of attributes to be included. (required)
    """
    Validate.dict_or_list_of_dicts(data, 'data')
    Validate.list(attributes, 'attributes')

    if isinstance(data, dict):
        return Dict.only_with(data, attributes)
    else:
        result = []
        for item in data:
            result.append(Dict.only_with(item, attributes))

def all_except(data, attributes):
    """
    Return a dictionary or list of dictionaries 
    with all the keys except the ones provided in target.

    Example Usage: "{{ data | all_except(['key1', 'key2']) }}"

    Option Parameters:
     - attributes: The list of attributes to be excluded. (required)
    """
    Validate.dict_or_list_of_dicts(data, 'data')
    Validate.list(attributes, 'attributes')

    if isinstance(data, dict):
        return Dict.all_except(data, attributes)
    else:
        result = []
        for item in data:
            result.append(Dict.all_except(item, attributes))

def to_querystring(data, keyAttr, valAttr=None, assignChar='=', joinChar='&'):
    """
    Convert a dictionary or list of dictionaries to a query string.

    Example Usage: "{{ data | aybars.helper.to_querystring('name', 'age', '=', '&') }}"

    Option Parameters:
     - keyAttr: The key attribute to be used in the query string. (required)
     - valAttr: The value attribute to be used in the query string. (optional)
     - assignChar: The character to be used between key and value. (optional | default: '=')
     - joinChar: The character to be used between key-value pairs. (optional | default: '&')
    """
    Validate.dict_or_list_of_dicts(data, 'data')

    if isinstance(data, dict):
        data = [data]

    result = []
    for item in data:
        if keyAttr in item:
            if valAttr and valAttr in item:
                result.append(f"{item[keyAttr]}{assignChar}{item[valAttr]}")
            else:
                result.append(f"{item[keyAttr]}")

    return joinChar.join(result)

def to_list_of_dicts(data, defaults={}):
    """
    Convert a dictionary of lists to a list of dictionaries.
    """
    Validate.dict(data, 'data')
    Validate.dict(defaults, 'defaults')
    
    firstKey = list(data.keys())[0]
    result = []

    for keyIndex, value in enumerate(data[firstKey]):
        new_item = defaults.copy()
        for dataKey in data.keys():
            new_item[dataKey] = data[dataKey][keyIndex]
        result.append(new_item)
        
    return result

def unique_by_attribute(data, attribute):
    seen = set()
    result = []
    for item in data:
        if attribute not in item:
            result.append(item)
        elif item.get(attribute) not in seen:
            result.append(item)
            seen.add(item.get(attribute))
    return result

def _unique_recursive(data, attribute, recurse=None):
    def get_nested_value(item, nested_key):
        keys = nested_key.split('.')
        value = item
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def set_nested_value(item, nested_key, value):
        keys = nested_key.split('.')
        d = item
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value

    for item in data:
        if isinstance(item, dict) and recurse:
            nested_value = get_nested_value(item, recurse)
            if isinstance(nested_value, list):
                unique_nested_value = unique_recursive(nested_value, attribute, recurse)
                set_nested_value(item, recurse, unique_nested_value)
    return unique_by_attribute(data, attribute)

def unique_recursive(data, attributes, recurse=None):
    Validate.list_of_dicts(data, 'data')
    
    if isinstance(attributes, str):
        attributes = [attributes]
    else:
        Validate.list(attributes, 'attributes')
    
    for attr in attributes:
        data = _unique_recursive(data, attr, recurse)

    return data

def replace_aliases(data, attributes, overwrite=False, removeAliases=False):
    Validate.dict_or_list_of_dicts(data, 'data')
    Validate.dict(attributes, 'attributes')

    rtrDict = False
    if isinstance(data, dict):
        data = [data]
        rtrDict = True
    
    result = data.copy()
    for itemKey, item in enumerate(data):
        for attr, aliases in attributes.items():
            aliases = aliases if isinstance(aliases, list) else [aliases]
            for alias in aliases:
                if alias in item:
                    if not attr in item or overwrite:
                        result[itemKey][attr] = item[alias]
                    if removeAliases:
                        del result[itemKey][alias]

    return result[0] if rtrDict else result

class FilterModule(object):
    def filters(self):
        return {
            'only_with': only_with,
            'all_except': all_except,
            'to_querystring': to_querystring,
            'unique_recursive': unique_recursive,
            'to_list_of_dicts': to_list_of_dicts,
            'replace_aliases': replace_aliases,
        }