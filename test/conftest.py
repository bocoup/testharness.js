import io
import json
import os

import html5lib
import pytest
from selenium import webdriver

_ENC = 'utf8'
_HERE = os.path.dirname(os.path.abspath(__file__))

def pytest_collect_file(path, parent):
    if path.ext.lower() == '.html':
        return HTMLItem(str(path), parent)

def pytest_configure(config):
    config.driver = webdriver.Firefox()
    config.add_cleanup(lambda: config.driver.quit())

class HTMLItem(pytest.Item, pytest.Collector):
    def __init__(self, fspath, parent):
        with io.open(fspath, encoding=_ENC) as f:
            markup = f.read()

        parsed = html5lib.parse(markup, namespaceHTMLElements=False)
        name = None
        self.expected = None

        for element in parsed.getiterator():
            if not name and element.tag == 'title':
                name = element.text
                continue
            if element.attrib.get('id') == 'expected':
                self.expected = element.text
                continue

        super(HTMLItem, self).__init__(name, parent)
        self.fspath = fspath

    def repr_failure(self, excinfo):
        return pytest.Collector.repr_failure(self, excinfo)

    def runtest(self):
        driver = self.session.config.driver

        driver.get('file://' + _HERE + '/harness.html')

        if self.expected is None:
            raise Exception('Expected value not declared')
        expected = json.loads(self.expected)

        actual = driver.execute_async_script('runTest("%s", "foo", arguments[0])' % self.fspath)

        actual["status"] = self._scrub_stack(actual["status"])
        actual["tests"] = map(self._scrub_stack, actual["tests"])

        print json.dumps(actual, indent=2)

        assert actual == expected

    @staticmethod
    def _scrub_stack(obj):
        copy = dict(obj)

        assert "stack" in obj

        if isinstance(obj["stack"], basestring):
            copy["stack"] = "(implementation-defined)"

        return copy
