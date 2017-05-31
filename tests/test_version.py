import unittest
import json

import flask
from flask_restful import Api
from resources import version


class TestVersion(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.API = Api(self.app)
        self.API.add_resource(version.Version, '/version', resource_class_kwargs={'filename': 'versiontest.json'})

    def test_get(self):
        response = self.app.test_client().get('/version')
        json_response = json.loads(response.get_data().decode("utf-8"))

        self.assertIn('version', json_response)
        self.assertRegex(json_response['version'], '^\d+\.\d+\.\d+')
        self.assertEqual(response.status_code, 200)
        self.assertIn('build_number', json_response)
        self.assertEqual(json_response['build_number'], 'unittest')


class TestVersionWithError(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.API = Api(self.app)
        self.API.add_resource(version.Version, '/version', resource_class_kwargs={'filename': 'NOTEXISTS.json'})

    def test_get(self):
        response = self.app.test_client().get('/version')
        json_response = json.loads(response.get_data().decode("utf-8"))

        self.assertIn('version', json_response)
        self.assertRegex(json_response['version'], '^\d+\.\d+\.\d+')
        self.assertEqual(response.status_code, 200)
        self.assertIn('build_number', json_response)
        self.assertEqual(json_response['build_number'], 'None')  # default when exception is caught


if __name__ == '__main__':
    unittest.main()
