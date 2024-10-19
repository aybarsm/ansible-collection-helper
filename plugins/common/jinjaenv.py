from __future__ import annotations
import jinja2
from ansible.errors import AnsiblePluginError
from ansible.plugins.filter.core import FilterModule as AnsibleFilterCore
from ansible.plugins.filter.encryption import FilterModule as AnsibleFilterEncryption
from ansible.plugins.filter.mathstuff import FilterModule as AnsibleFilterMathstuff
from ansible.plugins.filter.urls import FilterModule as AnsibleFilterUrls
from ansible.plugins.filter.urls import FilterModule as AnsibleFilterUrlsplit
from ansible.plugins.test.core import TestModule as AnsibleTestCore
from ansible.plugins.test.files import TestModule as AnsibleTestFiles
from ansible.plugins.test.mathstuff import TestModule as AnsibleTestMathstuff
from ansible.plugins.test.uri import TestModule as AnsibleTestUri

class JinjaEnv:
    def __init__(self):
        self.e = jinja2.Environment()
        self.e.filters.update(AnsibleFilterCore().filters())
        self.e.filters.update(AnsibleFilterEncryption().filters())
        self.e.filters.update(AnsibleFilterMathstuff().filters())
        self.e.filters.update(AnsibleFilterUrls().filters())
        self.e.filters.update(AnsibleFilterUrlsplit().filters())
        self.e.tests.update(AnsibleTestCore().tests())
        self.e.tests.update(AnsibleTestFiles().tests())
        self.e.tests.update(AnsibleTestMathstuff().tests())
        self.e.tests.update(AnsibleTestUri().tests())

    def validateTest(self, test):
        if not self.testExists(test):
            raise AnsiblePluginError(f"aybarsm::helper::common::jinjaenv - Test {test} does not exist.")

    def testExists(self, test):
        return test in self.e.tests
    
    def validateFilter(self, filter):
        if not self.filterExists(filter):
            raise AnsiblePluginError(f"aybarsm::helper::common::jinjaenv - Filter {filter} does not exist.")

    def filterExists(self, filter):
        return filter in self.e.filters
    
    def test(self, test, *args):
        self.validateTest(test)
        return self.e.tests[test](*args)
    
    def filter(self, filter, *args):
        self.validateFilter(filter)
        return self.e.filters[filter](*args)