from jinja2.filters import pass_environment
from ansible.errors import AnsibleFilterError
from ..tools import Tools

# Example config:
# - attribute: state
#     value: absent
#     else: present
#     when:
#         - ['autoremove', 'defined']
#         - ['autoremove', 'true']
#     logic: and

@pass_environment
def setattr_conditional(environment, data, configs):
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
    
        data = Tools.set_attr_conditional(environment, data, cnf)

    return data
        
class FilterModule(object):
    def filters(self):
        return {
            'setattr_conditional': setattr_conditional,
        }