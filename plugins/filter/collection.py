import hashlib
from ansible.errors import AnsibleFilterError

def hash_md5(content):
    return hashlib.md5(str(content).encode()).hexdigest()

def data_get(data, key, default=None):
    if key is None:
        return data

    if isinstance(key, str):
        key = key.split('.')

    for i, segment in enumerate(key):
        key.pop(i)

        if segment is None:
            return data

        if segment == '*':
            if not isinstance(data, (list, dict)):
                return default

            result = []

            for item in data:
                result.append(data_get(item, key))

            return [item for sublist in result for item in sublist] if '*' in key else result

        if segment == '\\*':
            segment = '*'
        elif segment == '\\{first}':
            segment = '{first}'
        elif segment == '{first}':
            if isinstance(data, dict):
                segment = next(iter(data))
            elif isinstance(data, list):
                segment = 0
            else:
                return default
        elif segment == '\\{last}':
            segment = '{last}'
        elif segment == '{last}':
            if isinstance(data, dict):
                segment = next(reversed(data))
            elif isinstance(data, list):
                segment = len(data) - 1
            else:
                return default

        if isinstance(data, dict) and segment in data:
            data = data[segment]
        elif isinstance(data, list) and isinstance(segment, int) and 0 <= segment < len(data):
            data = data[segment]
        else:
            return default

    return data

def data_set(data, key, value, overwrite=True):
    if isinstance(key, str):
        segments = key.split('.')
    else:
        segments = key

    segment = segments.pop(0)

    if segment == '*':
        if not isinstance(data, (list, dict)):
            data = []

        if segments:
            if isinstance(data, dict):
                keys = list(data.keys())
                for k in keys:
                    data[k] = data_set(data[k], segments.copy(), value, overwrite)
            elif isinstance(data, list):
                for i in range(len(data)):
                    data[i] = data_set(data[i], segments.copy(), value, overwrite)
        elif overwrite:
            if isinstance(data, dict):
                for k in data:
                    data[k] = value
            elif isinstance(data, list):
                for i in range(len(data)):
                    data[i] = value

    elif isinstance(data, dict):
        if segments:
            if segment not in data:
                data[segment] = {}
            data[segment] = data_set(data[segment], segments.copy(), value, overwrite)
        elif overwrite or segment not in data:
            data[segment] = value

    elif isinstance(data, list):
        if segment.isdigit():
            index = int(segment)
            if segments:
                if index >= len(data):
                    data.extend([{}] * (index - len(data) + 1))
                data[index] = data_set(data[index], segments.copy(), value, overwrite)
            elif overwrite or index >= len(data) or data[index] is None:
                if index >= len(data):
                    data.extend([None] * (index - len(data) + 1))
                data[index] = value

    else:
        data = {}
        if segments:
            data[segment] = data_set({}, segments.copy(), value, overwrite)
        elif overwrite:
            data[segment] = value

    return data

def data_forget(data, key):
    if isinstance(key, str):
        segments = key.split('.')
    else:
        segments = key

    segment = segments.pop(0)

    if segment == '*' and isinstance(data, (list, dict)):
        if segments:
            if isinstance(data, dict):
                for k in list(data.keys()):
                    data_forget(data[k], segments.copy())
            elif isinstance(data, list):
                for i in range(len(data)):
                    data_forget(data[i], segments.copy())
    elif isinstance(data, dict):
        if segments and segment in data:
            data_forget(data[segment], segments.copy())
        elif segment in data:
            del data[segment]
    elif isinstance(data, list) and segment.isdigit():
        index = int(segment)
        if segments and 0 <= index < len(data):
            data_forget(data[index], segments.copy())
        elif 0 <= index < len(data):
            del data[index]
    elif hasattr(data, segment):
        if segments:
            data_forget(getattr(data, segment), segments.copy())
        else:
            delattr(data, segment)

    return data

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
    
class FilterModule(object):
    def filters(self):
        return {
            'data_get': data_get,
            'data_set': data_set,
            'data_forget': data_forget,
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
        }