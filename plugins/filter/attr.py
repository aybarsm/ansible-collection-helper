from jinja2.filters import pass_environment
from ansible.errors import AnsibleFilterError
from ..tools import Tools
from .data import data_get, data_set

def _setattr(data, attribute, value, overwrite=False, deleteWhenNone=True):
    if not overwrite and attribute in data:
        return data
    if value is None and deleteWhenNone:
        data.pop(attribute, None)
    else:
        data[attribute] = value
    return data

@pass_environment
def setattr(environment, data, attributes, values, when=[], logic='and', overwrite=False, deleteWhenNone=True):
    if not isinstance(attributes, (str, list)):
        raise AnsibleFilterError("attributes should be a string or list")
    elif not isinstance(values, (str, list)):
        raise AnsibleFilterError("values should be a string or list")
    elif not isinstance(when, list) or (when and not all(isinstance(item, list) and len(item) >=2 for item in when)):
        raise AnsibleFilterError("when conditions should be list of lists with at least 2 elements")
    elif not logic in ['and', 'or']:
        raise AnsibleFilterError("logic should be 'and' or 'or'")

    if isinstance(attributes, str):
        attributes = [attributes]
    
    if isinstance(values, str):
        values = [values]

    if len(attributes) != len(values):
        raise AnsibleFilterError("attributes and values should have the same length")

    for attrIndex, attr in enumerate(attributes):
        if not when:
            data = _setattr(data, attr, values[attrIndex], overwrite, deleteWhenNone)
            continue
        
        conditionResults = []
        for condition in when:
            testResult = Tools.jinja_test(environment, data, condition)
            conditionResults.append(testResult)

            if (logic == 'or' and testResult) or (logic == 'and' and not testResult):
                break
            
        if (logic == 'or' and any(conditionResults)) or (logic == 'and' and all(conditionResults)):
            data = _setattr(data, attr, values[attrIndex], overwrite, deleteWhenNone)
        
    return data

class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
        }