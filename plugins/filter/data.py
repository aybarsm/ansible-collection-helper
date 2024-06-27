from ansible.errors import AnsibleFilterError

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

class FilterModule(object):
    def filters(self):
        return {
            'data_get': data_get,
            'data_set': data_set,
            'data_forget': data_forget,
        }