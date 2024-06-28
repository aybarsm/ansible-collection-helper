from ansible.errors import AnsibleFilterError

def _validate_list(data):
    if not isinstance(data, list):
        raise AnsibleFilterError("Data input should be a list")

def _validate_list_of_dicts(data):
    _validate_list(data)

    if not all(isinstance(item, dict) for item in data):
        raise AnsibleFilterError("Data input should be a list of dictionaries")

def keys_only(data, target):
    """Return only the keys of the given dictionary that are in the provided list."""
    if not isinstance(data, dict):
        raise AnsibleFilterError("keys_only filter expects a dictionary")
    if not isinstance(target, list):
        raise AnsibleFilterError("keys_only filter expects a list of keys to include")
    return [key for key in data.keys() if key in target]

def keys_except(data, target):
    """Return the keys of the given dictionary except the ones provided in target."""
    if not isinstance(data, dict):
        raise AnsibleFilterError("keys_except filter expects a dictionary")
    if not isinstance(target, list):
        raise AnsibleFilterError("keys_except filter expects a list of keys to exclude")
    return [key for key in data.keys() if key not in target]

def only_with(data, target):
    """Return a dictionary or list of dictionaries with only the keys that are in the provided list."""
    if not isinstance(target, list):
        raise AnsibleFilterError("only_with filter expects a list of keys to include")
    
    def filter_dict(dictionary):
        return {key: value for key, value in dictionary.items() if key in target}
    
    if isinstance(data, dict):
        return filter_dict(data)
    elif isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            return [filter_dict(item) for item in data]
        else:
            raise AnsibleFilterError("only_with filter expects a list of dictionaries")
    else:
        raise AnsibleFilterError("only_with filter expects a dictionary or a list of dictionaries")

def all_except(data, target):
    """Return a dictionary or list of dictionaries with all the keys except the ones provided in target."""
    if not isinstance(target, list):
        raise AnsibleFilterError("all_except filter expects a list of keys to exclude")
    
    def filter_dict(dictionary):
        return {key: value for key, value in dictionary.items() if key not in target}
    
    if isinstance(data, dict):
        return filter_dict(data)
    elif isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            return [filter_dict(item) for item in data]
        else:
            raise AnsibleFilterError("all_except filter expects a list of dictionaries")
    else:
        raise AnsibleFilterError("all_except filter expects a dictionary or a list of dictionaries")

def set_default(data, key, value, recurse=None):
    _validate_list_of_dicts(data)

    def set_default_recursively(data, key, value, recurse):
        for item in data:
            if isinstance(item, dict):
                if key not in item:
                    item[key] = value
                if recurse and recurse in item and isinstance(item[recurse], list):
                    set_default_recursively(item[recurse], key, value, recurse)
        return data

    return set_default_recursively(data, key, value, recurse)

def has_items(data):
    if isinstance(data, dict) or isinstance(data, list):
        return bool(data)
    else:
        raise AnsibleFilterError("Value is neither a list nor a dict")

def ensure_list(data):
    if isinstance(data, dict):
        return [{'key': k, 'value': v} for k, v in data.items()]
    elif isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            return data
        else:
            raise AnsibleFilterError("All items in the list should be dictionaries")
    else:
        raise AnsibleFilterError("Value should be a list or dictionary")

def flatten_query(data, keyAttribute, valAttribute=None, assignChar='=', joinChar=' '):
    if not isinstance(data, list):
        raise AnsibleFilterError("Input to flatten_query must be a list")

    result = []
    for item in data:
        if isinstance(item, dict) and keyAttribute in item:
            if valAttribute and valAttribute in item:
                result.append(f"{item[keyAttribute]}{assignChar}{item[valAttribute]}")
            else:
                result.append(f"{item[keyAttribute]}")
    return joinChar.join(result)

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
    if not (isinstance(data, list) or all(isinstance(entry, dict) for entry in data)):
        raise AnsibleFilterError("unique_recursive expects a list of dictionaries")
    
    if not isinstance(attributes, (str, list)):
        raise AnsibleFilterError("attributes should be a string or list")
    
    if isinstance(attributes, str):
        attributes = [attributes]
    
    for attr in attributes:
        data = _unique_recursive(data, attr, recurse)

    return data

def selectattr_defined(data, attributes, logic='and'):
    if not isinstance(data, list):
        raise AnsibleFilterError("selectattr_defined expects a list of dictionaries")

    if isinstance(attributes, str):
        attributes = [attributes]

    if not all(isinstance(attr, str) for attr in attributes):
        raise AnsibleFilterError("attributes should be a string or list of strings")

    if logic not in ['and', 'or']:
        raise AnsibleFilterError("logic should be either 'and' or 'or'")

    result = []
    for item in data:
        if isinstance(item, dict):
            if logic == 'and':
                if all(attr in item for attr in attributes):
                    result.append(item)
            elif logic == 'or':
                if any(attr in item for attr in attributes):
                    result.append(item)

    return result

def split_attr(data, srcAttr, dstAttr, searchStr, dstSideRight=True, srcRename=None, skipNotEligible=True):
    _validate_list(data)

    result = []
    for item in data:
        if not isinstance(item, dict):
            if skipNotEligible:
                result.append(item)
                continue
            else:
                raise AnsibleFilterError("Each item in the list should be a dictionary")
        
        if srcAttr in item and searchStr in item[srcAttr]:
            left, right = item[srcAttr].split(searchStr, 1)
            new_item = item.copy()
            if dstSideRight:
                new_item[dstAttr] = right
                if srcRename:
                    new_item[srcRename] = left
                    del new_item[srcAttr]
                else:
                    new_item[srcAttr] = left
            else:
                new_item[dstAttr] = left
                if srcRename:
                    new_item[srcRename] = right
                    del new_item[srcAttr]
                else:
                    new_item[srcAttr] = right
            result.append(new_item)
        else:
            result.append(item)

    return result

def join_attr(data, leftAttr, rightAttr, joinStr, dstAttr=None, overwrite=True, deleteSrcAttrs=False, skipNotEligible=True):
    _validate_list(data)

    if not dstAttr:
        dstAttr = leftAttr

    result = []
    for item in data:
        if not isinstance(item, dict):
            if skipNotEligible:
                result.append(item)
                continue
            else:
                raise AnsibleFilterError("Each item in the list should be a dictionary")

        if leftAttr in item and rightAttr in item and (dstAttr not in item or overwrite):
            new_item = item.copy()
            new_item[dstAttr] = f"{item[leftAttr]}{joinStr}{item[rightAttr]}"
            if deleteSrcAttrs and dstAttr != leftAttr:
                del new_item[leftAttr]
            if deleteSrcAttrs and dstAttr != rightAttr:
                del new_item[rightAttr]
            result.append(new_item)
        else:
            result.append(item)

    return result

class FilterModule(object):
    def filters(self):
        return {
            'keys_only': keys_only,
            'keys_except': keys_except,
            'only_with': only_with,
            'all_except': all_except,
            'set_default': set_default,
            'has_items': has_items,
            'ensure_list': ensure_list,
            'flatten_query': flatten_query,
            'unique_recursive': unique_recursive,
            'selectattr_defined': selectattr_defined,
            'split_attr': split_attr,
            'join_attr': join_attr,
        }