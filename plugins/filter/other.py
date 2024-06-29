from .jinja2 import jinja_env

def yardir(data):
    return jinja_env(data)

class FilterModule(object):
    def filters(self):
        return {
            'yardir': yardir,
        }