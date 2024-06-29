from jinja2.filters import pass_environment
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
    @pass_environment
    def jinja_test(environment, data, attribute, condition, value=None, undefinedValue=None):
        availableTests = list(environment.tests.keys())

        if condition not in availableTests:
            raise AnsibleFilterError(f"{condition} is not a valid Jinja test. Available Tests: {', '.join.availableTests}")
        
        if undefinedValue is None:
            undefinedValue = Tools.generate_unique_salt()

        item = data_get(data, attribute, undefinedValue)
        
        if condition == 'defined':
            return item != undefinedValue
        elif condition == 'undefined':
            return item == undefinedValue
        elif value is None:
            return environment.tests[condition](item)
        else:
            return environment.tests[condition](item, value)