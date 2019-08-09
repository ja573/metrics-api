from paste.fixture import TestApp
from nose.tools import *
from api import app
import os
import json


def create_t_app():
    middleware = []
    testApp = TestApp(app.wsgifunc(*middleware))
    return testApp


class TestCode():
    def test_broken_api(self):
        testApp = create_t_app()

        testApp.get('/non-existent-api-call', status=404)

    def test_unauth_post(self):
        testApp = create_t_app()

        payload = {}
        testApp.post('/events', payload, status=403)

    def test_auth_post_empty(self):
        testApp = create_t_app()

        token = os.environ.get("TOKEN")
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
        r = testApp.post('/events', params='{}', headers=headers, status=400)

    def test_auth_post_trivial(self):
        testApp = create_t_app()

        token = os.environ.get("TOKEN")
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
        data = {
            "work_uri": "info:doi:10.11647/obp.0020",
            "measure_uri":
              "https://metrics.operas-eu.org/world-reader/users/v1",
            "timestamp": "2019-01-01T01:00:00",
            "country_uri": "urn:iso:std:3166:-2:ES","value":"512"
        }
        params = json.dumps(data, indent=2)
        r = testApp.post('/events', params=params, headers=headers, status=200)

    def test_auth_post_readback(self):
        testApp = create_t_app()

        token = os.environ.get("TOKEN")
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
        data = {
            "work_uri": "info:doi:10.11647/obp.0020",
            "measure_uri":
              "https://metrics.operas-eu.org/world-reader/users/v1",
            "timestamp": "2019-01-01T01:00:00",
            "country_uri": "urn:iso:std:3166:-2:ES","value":"512"
        }
        params = json.dumps(data, indent=2)
        r = testApp.post('/events', params=params, headers=headers, status=200)

        results = json.loads(r.body)
        assert_equals(results["status"], "ok")
        print(results["data"][0]["event_id"])

#            # r.mustcontain('Hello, world!')
