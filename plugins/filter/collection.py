from __future__ import annotations
from ..common.tools import Validate, Dict, Convert
import os
import shlex
from ansible.module_utils.common.text.converters import to_text, to_native, to_bytes
from ansible.module_utils.common.collections import is_iterable
# from ansible.plugins.filter.mathstuff import intersect as ansible_intersect
from ansible_collections.ansible.builtin.plugins.filter.core import combine as ansible_combine

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

    isDataDict = Validate.isDict(data)

    for itemKey, item in enumerate(Convert.wrapList(data)):
        data[itemKey] = Dict.only_with(item, attributes)

    return data[0] if isDataDict else data

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

    isDataDict = Validate.isDict(data)

    for itemKey, item in enumerate(Convert.wrapList(data)):
        data[itemKey] = Dict.all_except(item, attributes)

    return data[0] if isDataDict else data

def to_querystring(data, keyAttr, valAttr=None, assignChar='=', joinChar='&', recurse=None, recurseIndentSteps=0, recurseIndentChar=' ', repeatJoinCharOnMainLevels=False):
    """
    Convert a dictionary or list of dictionaries to a query string.

    Example Usage: "{{ data | aybars.helper.to_querystring('name', 'age', '=', '&') }}"

    Option Parameters:
     - keyAttr: The key attribute to be used in the query string. (required)
     - valAttr: The value attribute to be used in the query string. (optional)
     - assignChar: The character to be used between key and value. (optional | default: '=')
     - joinChar: The character to be used between key-value pairs. (optional | default: '&')
     - recurse: The attribute to be used for recursion. (optional)
     - recurseIndentSteps: The number of steps to be used for indentation for child objects. (optional | default: 0)
     - recurseIndentChar: The character to be used for indentation. (optional | default: ' ')
     - repeatJoinCharOnMainLevels: Whether to repeat the join character on main levels. (optional | default: False)
    """
    Validate.dict_or_list_of_dicts(data, 'data')

    if isinstance(data, dict):
        data = [data]

    result = []

    def _to_querystring(innerData, level = 0):
        indent = recurseIndentChar * (level * recurseIndentSteps)
        for item in innerData:
            if keyAttr in item:
                if repeatJoinCharOnMainLevels and level == 0:
                    result.append('')
                if valAttr and valAttr in item:
                    result.append(f"{indent}{item[keyAttr]}{assignChar}{item[valAttr]}")
                else:
                    result.append(f"{indent}{item[keyAttr]}")

                if recurse and recurse in item and item[recurse]:
                    _to_querystring(item[recurse], level + 1)

    _to_querystring(data)

    return joinChar.join(result).strip(joinChar)

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

def unique_combinations(data, attrCombinations, skipMissing=True):
    """
    Return a list of dictionaries with unique attribute combinations.

    Example Usage: "{{ data | unique_combinations([['key1', 'key2'], ['key3', 'key4', 'key5']]) }}"

    Option Parameters:
     - attrCombinations: The list of attribute combinations to be checked. (required)
     - skipMissing: Whether to skip the items with missing attributes. (optional | default: True)
    """
    Validate.list_of_dicts(data, 'data')
    Validate.list_of_lists_or_tuples(attrCombinations, 'attrCombinations')

    result = []
    seen = set()
    for attrs in attrCombinations:
        attrs.sort()
        for item in data:
            if not Dict.has_all(item, attrs):
                if skipMissing:
                    continue
                else:
                    result.append(item)

            innerResult = []
            for attr in attrs:
                innerResult.append(Convert.to_string(item[attr], True))

            current_entry = Convert.to_md5_base64_encode(innerResult, True, True)
            if current_entry not in seen:
                result.append(item)
                seen.add(current_entry)

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
    if (Validate.isList(data) and len(data) == 0):
        return data

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

def remove_omitted(data):
    """
    Remove the omitted keys from a list.

    Example Usage: "{{ data | remove_omitted() }}"
    """
    if (Validate.isList(data) and len(data) > 0):
        for itemKey, item in enumerate(data):
            if Validate.isString(item) and item.startswith('__omit_place_holder__'):
                del data[itemKey]

    return data

def make_args(args):
    """
    """
    if Validate.isList(args) and len(args) > 0:
        args = remove_omitted(args)

    if is_iterable(args, include_strings=False):
        args = [to_native(arg, errors='surrogate_or_strict', nonstring='simplerepr') for arg in args]

    # if isinstance(args, (bytes, str)):
    #     args = shlex.split(to_text(args, errors='surrogateescape'))

    # args = [to_bytes(os.path.expanduser(os.path.expandvars(x)), errors='surrogate_or_strict') for x in args if x is not None]

    if isinstance(args, list):
        args = b" ".join([to_bytes(shlex.quote(x), errors='surrogate_or_strict') for x in args])
    else:
        args = to_bytes(args, errors='surrogate_or_strict')

    return args

def combine_reverse(*terms, **kwargs):
    """
    Combine the provided dicts in reverse order.

    Example Usage: "{{ data | aybarsm.helper.combine_reverse(dict1, dict2, dict3) }}"
    """
    terms_reversed = reversed(terms)
    return ansible_combine(*terms_reversed, **kwargs)

# def contains_all(data, values):
#     if not Validate.isList(values):
#         values = [values]

#     return len(list(set(data) & set(values))) == len(values)

class FilterModule(object):
    def filters(self):
        return {
            'only_with': only_with,
            'all_except': all_except,
            'to_querystring': to_querystring,
            'unique_recursive': unique_recursive,
            'to_list_of_dicts': to_list_of_dicts,
            'replace_aliases': replace_aliases,
            'unique_combinations': unique_combinations,
            'remove_omitted': remove_omitted,
            'make_args': make_args,
            'combine_reverse': combine_reverse,
            # 'contains_all': contains_all,
        }