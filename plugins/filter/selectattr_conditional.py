from jinja2.filters import pass_environment
from ansible.errors import AnsibleFilterError
from ..common.tools import Tools

# Example config:
# - attribute: state
#   value: absent
#   else: present
#   when:
#     - ['autoremove', 'defined']
#     - ['autoremove', 'true']
#   logic: and

@pass_environment
def selectattr_conditional(environment, data, configs):
    for cnf in configs:
        if not ('attribute' in cnf and 'value' in cnf and 'when' in cnf and 'logic' in cnf):
            raise AnsibleFilterError("Configuration should have 'attribute', 'value' keys, 'when' and 'logic' keys")
        elif not isinstance(cnf['when'], list) and not all(isinstance(item, list) and len(item) >=2 for item in cnf['when']):
            raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
        elif not cnf['logic'] in ['and', 'or']:
            raise AnsibleFilterError("logic should be 'and' or 'or'")
    
        data = Tools.set_attr_conditional(environment, data, cnf)

    return data
        
class FilterModule(object):
    def filters(self):
        return {
            'selectattr_conditional': selectattr_conditional,
        }