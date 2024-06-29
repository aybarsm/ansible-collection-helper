from jinja2 import Environment

def jinja_env(data):
    env = Environment()
    return env.tests['in']('deneme', ['hayir','deneme'])

class FilterModule(object):
    def filters(self):
        return {
            'jinja_env': jinja_env,
        }