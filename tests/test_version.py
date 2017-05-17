import unittest

import flask

from resources import version


class TestVersion(unittest.TestCase):
    def test_get(self):
        app = flask.Flask(__name__)
        with app.test_request_context(''):
            result = version.Version.get()

            self.assertIn('version',result)
            self.assertRegex(result['version'], '^\d+\.\d+\.\d+')


if __name__ == '__main__':
    unittest.main()
