from ansible.errors import AnsibleFilterError
from ..common.tools import Dict, JinjaEnv
from jinja2.filters import pass_environment

# Example config for setattr:
# List of dictionaries
# - attribute: state (required)
#   value: absent (required)
#   else: present (optional)
#   when: (optional)
#     - ['autoremove', 'defined']
#     - ['autoremove', 'true']
#   logic: and (optional | default is 'and')
#   overwrite: false (optional | default is False)
#   deleteWhenNone: false (optional | default is False)
# (If the value is set to be None either with 'value' or 'else' key, the attribute will be deleted if deleteWhenNone is True)

# Example config for selectattr and rejectattr:
# when: (required)
#   - ['state', 'defined']
#   - ['state', 'equalto', 'present']
# logic: and (optional | default is 'and')

# Example config for splitattr:
# List of dictionaries
# - srcAttr: name (required)
#   dstAttr: version (required)
#   search: = (required)
#   overwrite: true (optional | default is True)
#   dstSide: right (optional | default is 'right')
#   renameSrcAttr: package (optional)
#   dstDefault: None (optional)
#   when: (optional)
#     - ['name', 'defined']
#     - ['version', 'undefined']
#   logic: and (optional | default is 'and')

# Example config for joinattr:
# List of dictionaries
# - leftAttr: name (required)
#   rightAttr: version (required)
#   join: = (required)
#   overwrite: true (optional | default is True)
#   dstAttr: name (optional | default is leftAttr)
#   deleteSrcAttrs: False (optional | default is False)
#   when: (optional)
#     - ['name', 'defined']
#     - ['version', 'undefined']
#   logic: and (optional | default is 'and')

class Attr:
    def __init__(self, jinja_env, action, data, configs, required, cnf_defaults={}):
        self.jinja = JinjaEnv(jinja_env)
        self.action = action
        self.data = data
        self.configs = configs
        self.required = required
        self.cnf_defaults = cnf_defaults
        
        self.validate_and_prep()

        if action in ['select', 'reject']:
            self.result = []
        else:
            self.result = data.copy()

    def validate_and_prep(self):
        if not (isinstance(self.data, list) or all(isinstance(item, dict) for item in self.data)):
            raise AnsibleFilterError("data must be a list of dictionaries")
        
        for cnf in self.configs:
            if not isinstance(cnf, dict):
                raise AnsibleFilterError("configuration elements must be dictionaries")
            
            if not all(key in cnf for key in self.required):
                raise AnsibleFilterError(f"configuration elements must have all required keys: {', '.join(self.required)}")
            
            if 'attribute' not in cnf or 'value' not in cnf:
                raise AnsibleFilterError("configuration elements must have 'attribute' and 'value' keys")

            if 'when' in cnf:
                if not isinstance(cnf['when'], list) or (not all(isinstance(condition, list) and len(condition) >=2 for condition in cnf['when'])):
                    raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
            
            if 'logic' in cnf and not cnf['logic'] in ['and', 'or']:
                raise AnsibleFilterError("logic should be 'and' or 'or'")
            
    def validate_select_or_reject(self):
        if not isinstance(self.configs, dict):
            raise AnsibleFilterError("configuration should be a dictionary")
        elif not 'when' in self.configs:
            raise AnsibleFilterError("configuration should have 'when' key")
        elif not isinstance(self.configs['when'], list) or (not all(isinstance(condition, list) and len(condition) >=2 for condition in self.configs['when'])):
            raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
        elif 'logic' in self.configs and not self.configs['logic'] in ['and', 'or']:
            raise AnsibleFilterError("logic should be 'and' or 'or'")
    
    def check_condition(self, dict_data, when, logic):
        conditionResults = []
        for condition in when:
            testResult = self.jinja.test_attr(dict_data, condition)
            conditionResults.append(testResult)

            if (logic == 'or' and testResult) or (logic == 'and' and not testResult):
                break
            
        return (logic == 'or' and any(conditionResults)) or (logic == 'and' and all(conditionResults))
    
    def result_select_or_reject(self, item, cnf):
        whenResult = self.check_condition(item, cnf['when'], cnf['logic'])
        
        if (self.action == 'select' and whenResult) or (self.action == 'reject' and not whenResult):
            self.result.append(item)

    def result_set(self, item, cnf):
        whenResult = True if not cnf['when'] else self.check_condition(item, cnf['when'], cnf['logic'])
        finalValue = cnf['else'] if 'else' in cnf and not whenResult else (cnf['value'] if whenResult else item[cnf['attribute']])

        return Dict.set_val(item, cnf['attribute'], finalValue, cnf['overwrite'], cnf['deleteWhenNone'])
    
    def run(self):
        for itemIndex, item in enumerate(self.data):
            for cnf in self.configs:
                if self.action == 'set':
                    self.result[itemIndex] = self.result_set(item, cnf)
                elif self.action in ['select', 'reject']:
                    self.result_select_or_reject(item, cnf)
        
        return self.result
    
def select_or_reject_attr(environment,data, configs, reject=False):
    required = ['when']
    cnf_defaults = {'logic': 'and'}
    
    action = 'select' if not reject else 'reject'
    attr = Attr(environment, 'set', data, configs, required, cnf_defaults)

    return attr.run()

@pass_environment      
def setattr(environment, data, configs):
    required = ['attribute', 'value']
    cnf_defaults = {'logic': 'and', 'when':[], 'overwrite': False, 'deleteWhenNone': False}
    
    attr = Attr(environment, 'set', data, configs, required, cnf_defaults)

    return attr.run()

@pass_environment
def selectattr(environment, data, configs):
    return select_or_reject_attr(environment, data, configs)

@pass_environment
def rejectattr(environment, data, configs):
    return select_or_reject_attr(environment, data, configs, True)

@pass_environment      
def splitattr(environment, data, configs):
    required = ['srcAttr', 'dstAttr', 'search']
    cnf_defaults = {'overwrite': True, 'dstSide': 'right', 'when': [], 'logic': 'and'}
    
    attr = Attr(environment, 'set', data, configs, required, cnf_defaults)

    return attr.run()

@pass_environment      
def joinattr(environment, data, configs):
    required = ['leftAttr', 'rightAttr', 'join']
    cnf_defaults = {'overwrite': True, 'deleteSrcAttrs': False, 'when': [], 'logic': 'and'}
    
    attr = Attr(environment, 'set', data, configs, required, cnf_defaults)

    return attr.run()

class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
            'selectattr': selectattr,
            'rejectattr': rejectattr,
        }