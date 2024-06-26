import json

def is_valid_json_object(data):
    try:
        parsed_value = json.loads(data)
        if isinstance(parsed_value, dict):
            return True
        return False
    except (ValueError, TypeError):
        return False

def is_valid_json_array(data):
    try:
        parsed_data = json.loads(data)
        if isinstance(parsed_data, list):
            return True
        return False
    except (ValueError, TypeError):
        return False
    
def is_valid_json(data):
    return is_valid_json_object(data) or is_valid_json_array(data)

class FilterModule(object):
    def filters(self):
        return {
            'is_valid_json_object': is_valid_json_object,
            'is_valid_json_array': is_valid_json_array,
            'is_valid_json': is_valid_json,
        }