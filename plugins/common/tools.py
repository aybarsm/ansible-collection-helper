from ansible.errors import AnsibleFilterError
from jinja2.filters import pass_environment

@pass_environment
def _get_jinja_env(environment):
    return environment

class Tools:    
    @staticmethod
    def merge_dicts(baseDict, *args):
        newDict = baseDict.copy()

        for arg in args:
            newDict.update(arg)
        
        return newDict
    
    @staticmethod
    def jinja_env():
        return _get_jinja_env()
    
    @staticmethod
    def jinja_test(data, condition):
        if len(condition) < 2:
            raise AnsibleFilterError("Condition should have at least 2 elements")
        
        jinja_env = Tools.jinja_env()
        test = condition[1]
        availableTests = list(jinja_env.tests.keys())

        if test not in availableTests:
            raise AnsibleFilterError(f"{test} is not a valid Jinja test. Available Tests: {', '.join.availableTests}")
        
        attribute = condition[0]
        value = condition[2] if len(condition) >= 3 else None

        if test == 'defined':
            return attribute in data
        elif test == 'undefined':
            return attribute not in data
        elif value is None:
            return jinja_env.tests[test](data[attribute])
        else:
            return jinja_env.tests[test](value, data[attribute])
    
    @staticmethod
    def setattr(data_dict, attribute, value, overwrite=False, deleteWhenNone=False):
        if not overwrite and attribute in data_dict:
            return data_dict
        if value is None and deleteWhenNone:
            data_dict.pop(attribute)
        else:
            data_dict[attribute] = value
        return data_dict
    
    @staticmethod
    def set_attr_conditional(environment, data, config):            
        config = Tools.merge_dicts({'when': [], 'logic': 'and', 'overwrite': False, 'deleteWhenNone': True}, config)
        
        if not config['when']:
            return Tools.set_attr_val(data, config['attribute'], config['value'], config['overwrite'], config['deleteWhenNone'])
            
        conditionResults = []
        for condition in config['when']:
            testResult = Tools.jinja_test(environment, data, condition)
            conditionResults.append(testResult)

            if (config['logic'] == 'or' and testResult) or (config['logic'] == 'and' and not testResult):
                break
            
        if (config['logic'] == 'or' and any(conditionResults)) or (config['logic'] == 'and' and all(conditionResults)):
            return Tools.set_attr_val(data, config['attribute'], config['value'], config['overwrite'], config['deleteWhenNone'])
        elif 'else' in config:
            return Tools.set_attr_val(data, config['attribute'], config['else'], config['overwrite'], config['deleteWhenNone'])
    
        return data

    @staticmethod
    def select_or_reject_attr_conditional(environment, data, config, negate=False):
        conditionResults = []
        for condition in config['when']:
            testResult = Tools.jinja_test(environment, data, condition)
            if negate:
                testResult = not testResult
            conditionResults.append(testResult)

            if (config['logic'] == 'or' and testResult) or (config['logic'] == 'and' and not testResult):
                break
            
        if (config['logic'] == 'or' and any(conditionResults)) or (config['logic'] == 'and' and all(conditionResults)):
            return data
    
        return False
