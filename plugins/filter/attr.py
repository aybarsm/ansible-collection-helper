from ansible.errors import AnsibleFilterError
from ..common.tools import Dict, JinjaEnv
from jinja2.filters import pass_environment

# Example config:
# - attribute: state (required for setattr)
#   value: absent (required for setattr)
#   else: present (optional for setattr)
#   when: (required for selectattr && rejectattr | optional for setattr)
#     - ['autoremove', 'defined']
#     - ['autoremove', 'true']
#   logic: and (optional for setattr && selectattr && rejectattr | default is 'and')
#   overwrite: false (optional for setattr | default is False)
#   deleteWhenNone: false (optional for setattr | default is False)
# (If the value is set to be None either with 'value' or 'else' key, the attribute will be deleted if deleteWhenNone is True)

class Attr:
    def __init__(self, action, data, configs, jinja_env, required=[], defaults_head={}, defaults_tail={}):
        self.action = action
        self.data = data
        self.configs = configs
        self.required = required
        self.defaults_head = defaults_head
        self.defaults_tail = defaults_tail
        self.jinja = JinjaEnv(jinja_env)
        self.result = []
        self.prep_configs()
        self.common_validation()

    def prep_configs(self):
        self.configs = list(map(lambda x: Dict.merge(self.defaults_head, x, self.defaults_tail), self.configs))
    
    def common_validation(self):
        if not (isinstance(self.data, list) or all(isinstance(item, dict) for item in self.data)):
            raise AnsibleFilterError("self.data should be a list of dictionaries")
        elif not isinstance(self.configs, list) or not all(isinstance(item, dict) for item in self.configs):
            raise AnsibleFilterError("self.configs should be a list of dictionaries")
        elif not all(len(list(cnf.keys() & set(self.required))) == len(self.required) for cnf in self.configs):
            raise AnsibleFilterError(f"Configuration should have {', '.join(self.required)} keys")
        elif 'when' in self.required and not all('when' in cnf for cnf in self.configs):
            raise AnsibleFilterError("when key is self.required in all configurations")
        elif 'when' in self.required and not all(isinstance(cnf['when'], list) and all(isinstance(item, list) and len(item) >=2 for item in cnf['when']) for cnf in self.configs):
            raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
        elif not all(cnf['logic'] in ['and', 'or'] for cnf in self.configs):
            raise AnsibleFilterError("logic should be 'and' or 'or'")
        elif not all(isinstance(cnf['overwrite'], bool) for cnf in self.configs):
            raise AnsibleFilterError("overwrite should be boolean")
        elif not all(isinstance(cnf['deleteWhenNone'], bool) for cnf in self.configs):
            raise AnsibleFilterError("deleteWhenNone should be boolean")
    
    def check_condition(self, dict_data, when, logic):
        conditionResults = []
        for condition in when:
            testResult = self.jinja.test_attr(dict_data, condition)
            conditionResults.append(testResult)

            if (logic == 'or' and testResult) or (logic == 'and' and not testResult):
                break
            
        return (logic == 'or' and any(conditionResults)) or (logic == 'and' and all(conditionResults))
    
    def run(self):
        for item in self.data:
            for cnf in self.configs:
                if 'when' in cnf:
                    whenResult = self.check_condition(item, cnf['when'], cnf['logic'])
                
                if (self.action == 'select' and whenResult) or (self.action == 'reject' and not whenResult):
                    self.result.append(item)
                elif self.action == 'set':
                    if 'when' in cnf:
                        finalValue = cnf['value'] if whenResult else cnf['else']
                        item = Dict.set_val(item, cnf['attribute'], finalValue, cnf['overwrite'], cnf['deleteWhenNone'])

                    self.result.append(item)
        
        return self.result
    
def select_or_reject_attr(environment,data, configs, reject=False):
    cnf_required = ['when']
    cnf_defaults_head = {'logic': 'and'}
    cnf_defaults_tail = {'overwrite': False, 'deleteWhenNone': False}
    
    action = 'select' if not reject else 'reject'
    attr = Attr(action, data, configs, environment, cnf_required, cnf_defaults_head, cnf_defaults_tail)

    return attr.run()

@pass_environment      
def setattr(environment, data, configs):
    cnf_required = ['attribute', 'value']
    cnf_defaults_head = {'logic': 'and', 'when':[], 'overwrite': False, 'deleteWhenNone': False}
    
    attr = Attr('set', data, configs, environment, cnf_required, cnf_defaults_head)

    return attr.run()

@pass_environment
def selectattr(environment, data, configs):
    return select_or_reject_attr(environment, data, configs)

@pass_environment
def rejectattr(environment, data, configs):
    return select_or_reject_attr(environment, data, configs, True)

        
class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
            'selectattr': selectattr,
            'rejectattr': rejectattr,
        }