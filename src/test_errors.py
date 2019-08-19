from paste.fixture import TestApp
from nose.tools import *
from api import app


def test_error1():
    assert True


class TestCode():
    def test_index(self):
        middleware = []
        testApp = TestApp(app.wsgifunc(*middleware))
        r = testApp.get('/')
        assert_equal(r.status, 200)
        r.mustcontain('Hello, world!')
