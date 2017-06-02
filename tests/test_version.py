import json
import unittest

import flask
from ddt import ddt, data, unpack
from flask_restful import Api
from mock import patch

from resources import version


@ddt
class TestVersion(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)

    @data(
        # tests normal execution
        ('versiontest.json', 'unittest', False),
        # tests when version file is missing; error message is written to console when tested
        ('NOTEXISTS.json', 'None', True),
    )
    @unpack
    @patch('resources.version.logging')
    def test_get(self, filename, exp_build_number, exp_exception, mock_logging):
        api = Api(self.app)
        api.add_resource(version.Version, '/version', resource_class_kwargs={'filename': filename})

        response = self.app.test_client().get('/version')
        json_response = json.loads(response.get_data().decode("utf-8"))

        # Verify the response
        self.assertIn('version', json_response)
        self.assertRegex(json_response['version'], '^\d+\.\d+\.\d+')
        self.assertEqual(response.status_code, 200)
        self.assertIn('build_number', json_response)
        self.assertEqual(json_response['build_number'], exp_build_number)

        # Verify exception handling
        mock_logger = mock_logging.getLogger()
        if exp_exception:
            mock_logger.exception.assert_called_once()
        else:
            mock_logger.exception.assert_not_called()


if __name__ == '__main__':
    unittest.main()
