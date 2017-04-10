import io
import os

import html5lib
import pytest
from selenium import webdriver

_ENC = 'utf8'
_HERE = os.path.dirname(os.path.abspath(__file__))

def pytest_collect_file(path, parent):
    if path.ext.lower() == '.html':
        return HTMLItem(str(path), parent, 'foo')

def pytest_configure(config):
    config.driver = webdriver.Firefox()
    config.add_cleanup(lambda: config.driver.quit())

class HTMLItem(pytest.Item):
    def __init__(self, path, parent, markup):
        with io.open(path, encoding=_ENC) as f:
            markup = f.read()

        parsed = html5lib.parse(markup, namespaceHTMLElements=False)
        name = None
        self.expected = None

        for element in parsed.getiterator():
            if not name and element.tag == 'title':
                name = element.text
                continue
            if element.attrib.get('id') == 'expected':
                self.expected = element.attrib.get('id')
                continue

        super(HTMLItem, self).__init__(name, parent)

    def runtest(self):
        driver = self.session.config.driver

        driver.get('file://' + _HERE + '/harness.html')

        if self.expected is None:
            raise Exception('Expected value not declared')

        expected = json.loads(self.expected)

        print self.name

        #values = driver.execute_async_script('runTest("%s", "foo", arguments[0])' % self.name)

        #assert "status"in values["expected"]
        #assert "status" in values["actual"]

        #expected_status = values["expected"]["status"]
        #actual_status = HTMLItem.scrub_stack(values["actual"]["status"])

        #assert actual_status == expected_status

        #assert "tests" in values["expected"]
        #assert "tests" in values["actual"]

        #expected_tests = values["expected"]["tests"]
        #actual_tests = map(HTMLItem.scrub_stack, values["actual"]["tests"])

        #assert actual_tests == expected_tests

    @staticmethod
    def _scrub_stack(obj):
        copy = dict(obj)

        assert "stack" in obj

        if isinstance(obj["stack"], basestring):
            copy["stack"] = "(implementation-defined)"

        return copy
