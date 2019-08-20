import json
from nose.tools import assert_equals
from .testapp import App, AuthApp

TEST_EVENT = {
    "work_uri": "info:doi:10.11647/obp.0020",
    "measure_uri": "https://metrics.operas-eu.org/world-reader/users/v1",
    "timestamp": "2019-01-01T01:00:00",
    "country_uri": "urn:iso:std:3166:-2:ES",
    "value": 512
}


class TestCode():
    def __init__(self):
        self.app = App()
        self.authapp = AuthApp()

    def test_broken_api(self):
        self.app.get('/non-existent-api-call', status=404)

    def test_unauth_post(self):
        payload = {}
        self.app.post('/events', payload, status=403)

    def test_auth_post_empty(self):
        headers = self.authapp.auth_headers
        self.authapp.post('/events', params='{}', headers=headers, status=400)

    def test_auth_post_trivial(self):
        headers = self.authapp.auth_headers
        self.app.post('/events', params=json.dumps(TEST_EVENT),
                      headers=headers, status=200)

    def test_auth_post_readback(self):
        headers = self.authapp.auth_headers
        r = self.app.post('/events', params=json.dumps(TEST_EVENT),
                          headers=headers, status=200)

        results = json.loads(r.body.decode('utf-8'))
        assert_equals(results["status"], "ok")
        for key, value in TEST_EVENT.items():
            assert_equals(results["data"][0][key], TEST_EVENT[key])
