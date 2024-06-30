from ansible.errors import AnsibleFilterError
from ..common.tools import Tools

# Example config:
# - attribute: state (required for setattr && selectattr && rejectattr)
#   value: absent (required for setattr)
#   else: present (optional for setattr)
#   when: (required for selectattr && rejectattr | optional for setattr)
#     - ['autoremove', 'defined']
#     - ['autoremove', 'true']
#   logic: and (optional for setattr && selectattr && rejectattr | default is 'and')
#   overwrite: false (optional for setattr | default is False)
#   deleteWhenNone: false (optional for setattr | default is False)
# (If the value is set to be None either with 'value' or 'else' key, the attribute will be deleted if deleteWhenNone is True)

def _common_validation(data, configs, required=[]):
    if not (isinstance(data, list) or all(isinstance(item, dict) for item in data)):
        raise AnsibleFilterError("Data should be a list of dictionaries")
    elif not isinstance(configs, list) or not all(isinstance(item, dict) for item in configs):
        raise AnsibleFilterError("Configs should be a list of dictionaries")
    elif not all(len(list(cnf.keys() & set(required))) != len(required) for cnf in configs):
        raise AnsibleFilterError(f"Configuration should have {', '.join(required)} keys")
    elif 'when' in required and not all('when' in cnf for cnf in configs):
        raise AnsibleFilterError("when key is required in all configurations")
    elif 'when' in required and not all(isinstance(cnf['when'], list) and all(isinstance(item, list) and len(item) >=2 for item in cnf['when']) for cnf in configs):
        raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
    elif not all(cnf['logic'] in ['and', 'or'] for cnf in configs):
        raise AnsibleFilterError("logic should be 'and' or 'or'")
    elif not all(isinstance(cnf['overwrite'], bool) for cnf in configs):
        raise AnsibleFilterError("overwrite should be boolean")
    elif not all(isinstance(cnf['deleteWhenNone'], bool) for cnf in configs):
        raise AnsibleFilterError("deleteWhenNone should be boolean")
    
def _prep_configs(configs, defaults_head={}, defaults_tail={}):
    return list(map(lambda x: Tools.merge_dicts(defaults_head, x, defaults_tail), configs))

def check_condition(dict_data, when, logic):
    conditionResults = []
    for condition in when:
        testResult = Tools.jinja_test(dict_data, condition)
        conditionResults.append(testResult)

        if (logic == 'or' and testResult) or (logic == 'and' and not testResult):
            break
        
    return (logic == 'or' and any(conditionResults)) or (logic == 'and' and all(conditionResults))

def set_attr_val(dict_data, attribute, value, overwrite=False, deleteWhenNone=False):
    if not overwrite and attribute in dict_data:
        return dict_data
    if value is None and deleteWhenNone:
        dict_data.pop(attribute)
    else:
        dict_data[attribute] = value
    return dict_data

def select_or_reject_attr(data, configs, reject=False):
    cnf_defaults_head = {'logic': 'and'}
    cnf_defaults_tail = {'overwrite': False, 'deleteWhenNone': False}
    configs = _prep_configs(configs, cnf_defaults_head, cnf_defaults_tail)
    
    _common_validation(data, configs, ['attribute', 'when'])

    result = []

    for item in data:
        for cnf in configs:
            conditionStatus = check_condition(item, cnf['when'], cnf['logic'])
            
            if conditionStatus and not reject:
                result.append(item)

    return result
            
def setattr(data, configs):
    cnf_defaults_head = {'logic': 'and', 'overwrite': False, 'deleteWhenNone': False}
    configs = _prep_configs(configs, cnf_defaults_head)

    _common_validation(data, configs, ['attribute', 'value'])

    for itemIndex, item in enumerate(data):
        for cnf in configs:
            conditionStatus = check_condition(item, cnf['when'], cnf['logic'])
            
            if not conditionStatus and 'else' in cnf:
                continue
            
            finalValue = cnf['value'] if conditionStatus else cnf['else']
            data[itemIndex] = set_attr_val(item, cnf['attribute'], finalValue, cnf['overwrite'], cnf['deleteWhenNone'])

    return data


def selectattr(data, configs):
    return select_or_reject_attr(data, configs)

def rejectattr(data, configs):
    return select_or_reject_attr(data, configs, True)

        
class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
            'selectattr': selectattr,
            'rejectattr': rejectattr,
        }