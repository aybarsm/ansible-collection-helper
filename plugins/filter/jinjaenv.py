from jinja2.filters import pass_environment

@pass_environment
def jinja_env_new(environment, data):
    return environment.tests['in']('deneme', ['hayir','deneme'])

class FilterModule(object):
    def filters(self):
        return {
            'jinja_env_new': jinja_env_new,
        }