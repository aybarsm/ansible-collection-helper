import pickle
import json
import base64
from jinja2.filters import pass_context, pass_environment, make_attrgetter, async_select_or_reject
from ansible.errors import AnsibleFilterError
from ansible.template import Templar
from ..tools import Tools
from .data import data_get, data_set

@pass_environment
def setattr(environment, data, attributes, values, conditions=[], logic='and', strict=False):
    if not isinstance(attributes, (str, list)):
        raise AnsibleFilterError("attributes should be a string or list")
    elif not isinstance(values, (str, list)):
        raise AnsibleFilterError("values should be a string or list")
    elif not isinstance(conditions, list):
        raise AnsibleFilterError("conditions should be a list")

    if isinstance(attributes, str):
        attributes = [attributes]
    
    if isinstance(values, str):
        values = [values]

    if len(attributes) != len(values):
        raise AnsibleFilterError("attributes and values should have the same length")

    for attrIndex, attr in enumerate(attributes):
        if attr not in data:
            if strict:
                raise AnsibleFilterError(f"{attr} is not in the data")
            else:
                continue
            
        data = data_set(data, attr, values[attrIndex])
    
    return data

def to_md5(data):
    if not isinstance(data, str):
        raise AnsibleFilterError("data should be a string")
    
    return Tools.hash_md5(data)

# @pass_context
# async def make_jinja_getter(context, value, *args, **kwargs):
#     func = async_select_or_reject(context, value, args, kwargs, lambda x: x, False)
#     return func()

@pass_environment
def make_jinja_getter(environment, value, attribute):
    func = make_attrgetter(environment, attribute)
    return func()

@pass_context
def obj_serialize(context):
    return context
    # pickled_obj = pickle.dumps(Templar)
    # base64_obj = base64.b64encode(pickled_obj).decode('utf-8')
    # return json.dumps({'obj': base64_obj})
    # return json.dumps(environment.filters.__dict__)
    # return json.dumps(make_attrgetter.__dict__)
    # return AnsibleEnvironment.filters

class FilterModule(object):
    def filters(self):
        return {
            'setattr': setattr,
            'to_md5': to_md5,
            'make_jinja_getter': make_jinja_getter,
            'obj_serialize': obj_serialize,
        }