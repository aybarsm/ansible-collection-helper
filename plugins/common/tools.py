from ansible.errors import AnsibleFilterError
from ansible.plugins.test.core import TestModule as AnsibleTestModule
import hashlib
import base64
import json

class AnsTest:
    @staticmethod
    def isTruthy(*args, **kwargs):
        return AnsibleTestModule.tests['truthy'](*args, **kwargs)

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
    def isInt(data):
        return isinstance(data, int)
    
    @staticmethod
    def isFloat(data):
        return isinstance(data, float)
    
    @staticmethod
    def isBool(data):
        return isinstance(data, bool)
    
    @staticmethod
    def isNone(data):
        return data is None
    
    @staticmethod
    def isCallable(data):
        return callable(data)

    @staticmethod
    def isListOfDicts(data):
        return Validate.isList(data) and all(Validate.isDict(item) for item in data)

    @staticmethod
    def isListofLists(data):
        return Validate.isList(data) and all(Validate.isList(item) for item in data)

    @staticmethod
    def isLisOfTuples(data):
        return Validate.isList(data) and all(Validate.isTuple(item) for item in data)

    @staticmethod
    def isDictOfLists(data):
        return Validate.isDict(data) and all(Validate.isList(item) for item in data.values())

    @staticmethod
    def list(data, attrName):
        if not Validate.isList(data):
            raise AnsibleFilterError(f"{attrName} should be list")

    @staticmethod
    def tuple(data, attrName):
        if not Validate.isTuple(data):
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

    @staticmethod
    def list_of_lists_or_tuples(data, attrName):
        if not (Validate.isList(data) and all(Validate.isList(item) or Validate.isTuple(item) for item in data)):
            raise AnsibleFilterError(f"{attrName} should be list of lists or tuples")
    
    @staticmethod
    def dict_or_list(data, attrName):
        if not (Validate.isDict(data) or Validate.isList(data)):
            raise AnsibleFilterError(f"{attrName} should be dictionary or list")
    
    @staticmethod
    def dict_or_list_or_tuple(data, attrName):
        if not (Validate.isDict(data) or Validate.isList(data) or Validate.isTuple(data)):
            raise AnsibleFilterError(f"{attrName} should be dictionary or list or tuple")
    
    @staticmethod
    def require(required, data, forAll = True, attrName = ''):
        if not (Validate.isList(required) or Validate.isString(required) or Validate.isTuple(required)):
            raise AnsibleFilterError("Validate.require, required should be list, tuple or string")

        if Validate.isString(required):
            required = [required]
        
        results = []
        for req in required:
            req = req.lower().replace('_', '').replace('-', '')

            match req:
                case 'list':
                    results.append(Validate.isList(data))
                case 'tuple':
                    results.append(Validate.isTuple(data))
                case 'dict':
                    results.append(Validate.isDict(data))
                case 'string':
                    results.append(Validate.isString(data))
                case 'int' | 'integer':
                    results.append(Validate.isInt(data))
                case 'float':
                    results.append(Validate.isFloat(data))
                case 'bool' | 'boolean':
                    results.append(Validate.isBool(data))
                case 'none':
                    results.append(Validate.isNone(data))
                case 'listoflists' | 'listoflist':
                    results.append(Validate.isListofLists(data))
                case 'listofdicts' | 'listofdict':
                    results.append(Validate.isListOfDicts(data))
                case 'listoftuples' | 'listoftuple':
                    results.append(Validate.isLisOfTuples(data))
                case 'dictoflists' | 'dictoflist':
                    results.append(Validate.isDictOfLists(data))
                case _:
                    raise AnsibleFilterError(f"Validate.require, {req} is not a valid type to check.")
        
            if forAll and any(results):
                return True
        
        if attrName != '' and (forAll or not all(results)):
            raise AnsibleFilterError(f"{attrName} should be {', '.join(required)}")
        
        return all(results)
        
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
        elif test == 'in':
            return self.jinja_env.tests['in'](data[attribute], value)
        elif value is None:
            return self.jinja_env.tests[test](data[attribute])
        else:
            return self.jinja_env.tests[test](value, data[attribute])

class Str:
    @staticmethod
    def isJson(data, type='any'):
        if not Validate.isString(data):
            return False

        try:
            parsedData = json.loads(data)
            if type == 'object':
                return Validate.isDict(parsedData)
            elif type == 'array':
                return Validate.isList(parsedData)
            return True
        except (ValueError, TypeError):
            return False

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
    def _contains_flex(data, search, isAny = True):
        def has_item(item, lookup):
            return all(item.get(k) == v for k, v in lookup.items())
        
        if Validate.isListOfDicts(data):
            return any(has_item(item, search) for item in data) if isAny else all(has_item(item, search) for item in data)
        else:
            return has_item(data, search)
    
    @staticmethod
    def contains(data, search):
        return Dict._contains_flex(data, search)
    
    @staticmethod
    def allContains(data, search):
        return Dict._contains_flex(data, search, False)

    @staticmethod
    def where(data, search):
        isDataDict = Validate.isDict(data)
        data = Convert.wrapList(data)

        result = [item for item in data if Dict.contains(item, search)]

        if isDataDict:
            return result[0] if result else {}
        else:
            return result
    
    @staticmethod
    def firstWhere(data, search, default = None):
        result = Dict.where(data, search)
        return result[0] if result else default

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

class Convert:
    @staticmethod
    def to_string(data, trim=False):
        result = ''
        if isinstance(data, str):
            result = data
        elif isinstance(data, dict) or isinstance(data, list) or isinstance(data, tuple):
            result = Convert.to_json(data)
        else:
            result = str(data)

        return result.strip() if trim else result

    @staticmethod
    def to_md5(data):
        return hashlib.md5(str(data).encode()).hexdigest()

    @staticmethod
    def to_base64_encode(data):
        return base64.b64encode(data.encode()).decode()

    @staticmethod
    def to_base64_decode(data):
        return base64.b64decode(data).decode()

    @staticmethod
    def to_json(data):
        return json.dumps(data)

    @staticmethod
    def to_md5_base64_encode(data, to_string=False, trim=False):
        if to_string:
            data = Convert.to_string(data, trim)

        return Convert.to_base64_encode(Convert.to_md5(data))

    @staticmethod
    def wrapList(data):
        return data if isinstance(data, list) else [data]
