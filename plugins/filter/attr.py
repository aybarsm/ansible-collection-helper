from jinja2.filters import pass_environment
from ansible.errors import AnsibleFilterError
from ..tools import Tools
from .data import data_get, data_set

def setattr(data, attributes, values, when=[], logic='and', strict=False):
    if not isinstance(attributes, (str, list)):
        raise AnsibleFilterError("attributes should be a string or list")
    elif not isinstance(values, (str, list)):
        raise AnsibleFilterError("values should be a string or list")
    elif not isinstance(when, list):
        raise AnsibleFilterError("conditions should be a list")
    elif not logic in ['and', 'or']:
        raise AnsibleFilterError("logic should be 'and' or 'or'")

    if isinstance(attributes, str):
        attributes = [attributes]
    
    if isinstance(values, str):
        values = [values]

    if len(attributes) != len(values):
        raise AnsibleFilterError("attributes and values should have the same length")
    
    defaultSalt = Tools.generate_unique_salt()
    result = []

    for attrIndex, attr in enumerate(attributes):
        result.append({'attr': attr, 'value': data_get(data, attr)})
        if data_get(data, attr, defaultSalt) == defaultSalt:
            if strict:
                raise AnsibleFilterError(f"{attr} is not in one of the items in data")
            else:
                result.append(f"{attr} skipped stage 1")
                continue
        
        if when:
            for condition in when:
                if 2 not in condition:
                    condition[2] = None
                if Tools.jinja_test(data, attr, condition[0], condition[1], condition[2]):
                    data_set(data, attr, values[attrIndex])

    return [data, result]

@pass_environment
def get_filter(environment, data, filterName):
    return environment.filters[filterName]

# def setattr(data, attributes, values, when=[], logic='and', strict=False):
#     if not isinstance(attributes, (str, list)):
#         raise AnsibleFilterError("attributes should be a string or list")
#     elif not isinstance(values, (str, list)):
#         raise AnsibleFilterError("values should be a string or list")
#     elif not isinstance(when, list):
#         raise AnsibleFilterError("conditions should be a list")
#     elif not logic in ['and', 'or']:
#         raise AnsibleFilterError("logic should be 'and' or 'or'")

#     if isinstance(attributes, str):
#         attributes = [attributes]
    
#     if isinstance(values, str):
#         values = [values]

#     if len(attributes) != len(values):
#         raise AnsibleFilterError("attributes and values should have the same length")
    
#     defaultSalt = Tools.generate_unique_salt()
#     result = []

#     for item in data:
#         for attrIndex, attr in enumerate(attributes):
#             if data_get(item, attr, defaultSalt) == defaultSalt:
#                 if strict:
#                     raise AnsibleFilterError(f"{attr} is not in one of the items in data")
#                 else:
#                     result.append('skipped stage 1')
#                     continue
            
#             if when:
#                 for condition in when:
#                     if 2 not in condition:
#                         condition[2] = None
#                     if Tools.jinja_test(item, attr, condition[0], condition[1], condition[2]):
#                         data_set(item, attr, values[attrIndex])

#     return [data, result]

class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
            'get_filter': get_filter,
        }