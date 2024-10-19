from __future__ import annotations
from ansible.plugins.test.core import truthy as AnsibleTestTruthy

def generic_truthy(*args, **kwargs):
    # return AnsibleTestModule.tests(AnsibleTestModule)['truthy'](*args, **kwargs)
    return AnsibleTestTruthy(*args, **kwargs)

class TestModule(object):
    def tests(self):
        return {
            'generic_truthy': generic_truthy
        }