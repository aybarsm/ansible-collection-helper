from ansible.errors import AnsibleFilterError

class Validate:
    @staticmethod
    def isList(data):
        return isinstance(data, list)

    @staticmethod
    def isTuple(data):
        return isinstance(data, tuple)
    
    @staticmethod
    def isDict(data):
        return isinstance(data, dict)
    
    @staticmethod
    def isString(data):
        return isinstance(data, str)
    
    @staticmethod
    def isListOfDicts(data):
        return Validate.isList(data) and all(Validate.isDict(item) for item in data)
    
    @staticmethod
    def list(data, attrName):
        if not Validate.isList(data):
            raise AnsibleFilterError(f"{attrName} should be list")
    
    @staticmethod
    def tuple(data, attrName):
        if not Validate.isList(data):
            raise AnsibleFilterError(f"{attrName} should be tuple")
    
    @staticmethod
    def dict(data, attrName):
        if not Validate.isDict(data):
            raise AnsibleFilterError(f"{attrName} should be dictionary")
    
    @staticmethod
    def list_or_tuple(data, attrName):
        if not Validate.isList(data) and not Validate.isTuple(data):
            raise AnsibleFilterError(f"{attrName} should be list or tuple")
    
    @staticmethod
    def list_of_dicts(data, attrName):
        if not Validate.isListOfDicts(data):
            raise AnsibleFilterError(f"{attrName} should be list of dictionaries")
    
    @staticmethod
    def dict_of_lists(data, attrName):
        if not (Validate.isDict(data) and all(Validate.isList(item) for item in data.values())):
            raise AnsibleFilterError(f"{attrName} should be dictionary of lists")
    
    @staticmethod
    def dict_or_list_of_dicts(data, attrName):
        if not (Validate.isDict(data) or Validate.isListOfDicts(data)):
            raise AnsibleFilterError(f"{attrName} should be dictionary or list of dictionaries")

    @staticmethod
    def string(data, attrName):
        if not Validate.isString(data):
            raise AnsibleFilterError(f"{attrName} should be string")
    
    @staticmethod
    def list_of_strings(data, attrName):
        if not (Validate.isList(data) or all(isinstance(item, str) for item in data)):
            raise AnsibleFilterError(f"{attrName} should be list of strings")

class JinjaEnv:
    def __init__(self, jinja_env):
        self.jinja_env = jinja_env
    
    def get_env(self):
        return self.jinja_env
    
    def run_filter(self, filterName, *args, **kwargs):
        availableFilters = list(self.jinja_env.filters.keys())

        if not filterName in self.jinja_env.filters:
            raise AnsibleFilterError(f"{filterName} is not a valid Jinja filter. Available Filters: {', '.join(availableFilters)}")
        
        return self.jinja_env.filters[filterName](*args, **kwargs)
    
    def run_test(self, testName, *args, **kwargs):
        availableTests = list(self.jinja_env.tests.keys())
        if not testName in self.jinja_env.tests:
            raise AnsibleFilterError(f"{testName} is not a valid Jinja test. Available Tests: {', '.join(availableTests)}")
        
        return self.jinja_env.tests[testName](*args, **kwargs)

    def test_attr(self, data, condition):
        if len(condition) < 2:
            raise AnsibleFilterError("Condition should have at least 2 elements")

        test = condition[1]
        availableTests = list(self.jinja_env.tests.keys())

        if test not in availableTests:
            raise AnsibleFilterError(f"{test} is not a valid Jinja test. Available Tests: {', '.join.availableTests}")
        
        attribute = condition[0]
        value = condition[2] if len(condition) >= 3 else None

        if test == 'defined':
            return attribute in data
        elif test == 'undefined':
            return attribute not in data
        elif value is None:
            return self.jinja_env.tests[test](data[attribute])
        else:
            return self.jinja_env.tests[test](value, data[attribute])
    
class Dict:    
    @staticmethod
    def merge(baseDict, *args):
        newDict = baseDict.copy()

        for arg in args:
            newDict.update(arg)
        
        return newDict

    @staticmethod
    def set_attr(dict_data, attribute, value, overwrite=False, deleteWhenNone=False):
        if not overwrite and attribute in dict_data:
            return dict_data
        if value is None and deleteWhenNone:
            dict_data.pop(attribute)
        else:
            dict_data[attribute] = value
        return dict_data
    
    @staticmethod
    def del_attr(dict_data, attribute):
        if attribute in dict_data:
            dict_data.pop(attribute)
        return dict_data
    
    @staticmethod
    def filter(dict_data, callback):
        return {key: value for key, value in dict_data.items() if callback(key, value)}

    @staticmethod
    def only_with(dict_data, attributes):
        return Dict.filter(dict_data, lambda key, value: key in attributes)
    
    @staticmethod
    def all_except(dict_data, attributes):
        return Dict.filter(dict_data, lambda key, value: key not in attributes)
        
    @staticmethod
    def has_any_or_all(hasAll, dict_data, attributes):
        if isinstance(attributes, str):
            attributes = [attributes]
        
        return all(attr in dict_data for attr in attributes) if hasAll else any(attr in dict_data for attr in attributes)
    
    @staticmethod
    def has_all(dict_data, attributes):
        return Dict.has_any_or_all(True, dict_data, attributes)

    @staticmethod
    def has_any(dict_data, attributes):
        return Dict.has_any_or_all(False, dict_data, attributes)
    
    @staticmethod
    def when(jinja, dict_data, when, logic):
        if not when:
            return True
        
        conditionResults = []
        for condition in when:
            testResult = jinja.test_attr(dict_data, condition)
            conditionResults.append(testResult)

            if (logic == 'or' and testResult) or (logic == 'and' and not testResult):
                break
            
        return (logic == 'or' and any(conditionResults)) or (logic == 'and' and all(conditionResults))