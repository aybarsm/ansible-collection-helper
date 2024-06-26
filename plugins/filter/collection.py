from ansible.errors import AnsibleFilterError

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
    if not isinstance(data, list):
        raise AnsibleFilterError(f"Expected a list but got {type(data)}")

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

def unique_recursive(data, attribute, recurse=None):
    def unique_by_attr(items):
        seen = set()
        result = []
        for item in items:
            if item.get(attribute) not in seen:
                result.append(item)
                seen.add(item.get(attribute))
        return result

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

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and recurse:
                nested_value = get_nested_value(item, recurse)
                if isinstance(nested_value, list):
                    unique_nested_value = unique_recursive(nested_value, attribute, recurse)
                    set_nested_value(item, recurse, unique_nested_value)
        return unique_by_attr(data)
    else:
        raise AnsibleFilterError("unique_recursive expects a list of dictionaries")

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
        }