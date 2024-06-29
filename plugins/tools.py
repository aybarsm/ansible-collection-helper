from ansible.errors import AnsibleFilterError
from .filter.data import data_get
import hashlib
import uuid
import datetime

class Tools:

    @staticmethod
    def hash_md5(content):
        return hashlib.md5(str(content).encode()).hexdigest()

    @staticmethod
    def uuid_4():
        return str(uuid.uuid4())
    
    @staticmethod
    def timestamp_iso(format="%Y-%m-%dT%H:%M:%SZ", UTC=True):
        if UTC:
            return datetime.datetime.now(datetime.UTC).strftime(format)
        return datetime.datetime.now().strftime(format)
    
    @staticmethod
    def generate_unique_salt(seperator="|", ts_format="%Y-%m-%dT%H:%M:%S.%fZ"):
        return str(Tools.timestamp_iso(format=ts_format) + seperator + Tools.uuid_4())
    
    @staticmethod
    def jinja_test(environment, data, condition):
        if len(condition) < 2:
            raise AnsibleFilterError("Condition should have at least 2 elements")
        
        test = condition[1]
        availableTests = list(environment.tests.keys())

        if test not in availableTests:
            raise AnsibleFilterError(f"{test} is not a valid Jinja test. Available Tests: {', '.join.availableTests}")
        
        attribute = condition[0]
        value = condition[2] if len(condition) >= 3 else None

        if test == 'defined':
            return attribute in data
        elif test == 'undefined':
            return attribute not in data
        elif value is None:
            return environment.tests[test](data[attribute])
        else:
            return environment.tests[test](value, data[attribute])
