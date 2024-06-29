from jinja2.filters import pass_environment
import dpath

@pass_environment
def data_get(environment, data, path):
    # return dpath.get(data, path)
    return environment.filters['json_query'](data, path)

def data_set(data, path, value):
    dpath.set(data, path, value)
    return data

def data_forget(data, path):
    dpath.delete(data, path)
    return data

class FilterModule(object):
    def filters(self):
        return {
            'data_get': data_get,
            'data_set': data_set,
            'data_forget': data_forget,
        }