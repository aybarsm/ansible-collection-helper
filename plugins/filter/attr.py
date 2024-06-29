from jinja2.filters import pass_environment
from ansible.errors import AnsibleFilterError
from ..tools import Tools

def _set_attribute_value(data, attribute, value, overwrite=False, deleteWhenNone=True):
    if not overwrite and attribute in data:
        return data
    if value is None and deleteWhenNone:
        data.pop(attribute)
    else:
        data[attribute] = value
    return data

# Example config:
# - attribute: state
#     value: absent
#     else: present
#     when:
#         - ['autoremove', 'defined']
#         - ['autoremove', 'true']
#     logic: and

@pass_environment
def setattr_config(environment, data, configs):
    for cnf in configs:
        if not ('attribute' in cnf and 'value' in cnf):
            raise AnsibleFilterError("Configuration should have 'attribute' and 'value' keys")
        elif 'when' in cnf and not isinstance(cnf['when'], list) and not all(isinstance(item, list) and len(item) >=2 for item in cnf['when']):
            raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
        elif 'logic' in cnf and not cnf['logic'] in ['and', 'or']:
            raise AnsibleFilterError("logic should be 'and' or 'or'")
        elif 'overwrite' in cnf and not isinstance(cnf['overwrite'], bool):
            raise AnsibleFilterError("overwrite should be boolean")
        elif 'deleteWhenNone' in cnf and not isinstance(cnf['deleteWhenNone'], bool):
            raise AnsibleFilterError("deleteWhenNone should be boolean")
        
        cnf = Tools.merge_dicts({'when': [], 'logic': 'and', 'overwrite': False, 'deleteWhenNone': True}, cnf)
        
        if not cnf['when']:
            data = _set_attribute_value(data, cnf['attribute'], cnf['value'], cnf['overwrite'], cnf['deleteWhenNone'])
            continue

        conditionResults = []
        for condition in cnf['when']:
            testResult = Tools.jinja_test(environment, data, condition)
            conditionResults.append(testResult)

            if (cnf['logic'] == 'or' and testResult) or (cnf['logic'] == 'and' and not testResult):
                break
            
        if (cnf['logic'] == 'or' and any(conditionResults)) or (cnf['logic'] == 'and' and all(conditionResults)):
            data = _set_attribute_value(data, cnf['attribute'], cnf['value'], cnf['overwrite'], cnf['deleteWhenNone'])
        elif 'else' in cnf:
            data = _set_attribute_value(data, cnf['attribute'], cnf['else'], cnf['overwrite'], cnf['deleteWhenNone'])
    
    return data
        
class FilterModule(object):
    def filters(self):
        return {
            'setattr_config': setattr_config,
        }