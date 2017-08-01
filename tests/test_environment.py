#!/usr/bin/env python3

import io
import unittest

from ddt import ddt, data, unpack
from mock import patch, MagicMock

from helpers import environment

TEST_YAML_DATA = {
    'the_default_env': {
        'property1': 'the first default property',
        'property2': 'the second default property',
        'property_int': 1234
    },
    'the_other_env': {
        'property1': 'the first other property',
        'property2': 'the second other property',
        'property_int': 567
    }
}

DEFAULT_ENV_VARS = {
    'ENVIRONMENT': 'the_default_env',
    'MONGODB_URI': 'the_mongodb_uri/Match',
}
OTHER_ENV_VARS = {
    'ENVIRONMENT': 'the_other_env',
    'MONGODB_URI': 'the_mongodb_uri/Match',
}

@ddt
class EnvironmentTests(unittest.TestCase):

    def setUp(self):
        yaml_patcher = patch('helpers.environment.yaml')
        self.addCleanup(yaml_patcher.stop)
        self.mock_yaml = yaml_patcher.start()
        self.mock_yaml.safe_load.return_value = TEST_YAML_DATA

        logging_patcher = patch('helpers.environment.logging')
        self.addCleanup(logging_patcher.stop)
        self.mock_logger = logging_patcher.start().getLogger()

        os_patcher = patch('helpers.environment.os')
        self.addCleanup(os_patcher.stop)
        self.mock_os = os_patcher.start()
        self.mock_os.environ = DEFAULT_ENV_VARS

        open_patcher = patch('helpers.environment.open')
        self.addCleanup(open_patcher.stop)
        self.mock_open = open_patcher.start()
        self.mock_open.return_value = MagicMock(spec=io.IOBase)

    def tearDown(self):
        environment.Environment._drop()

    @data(
        (DEFAULT_ENV_VARS,),
        (OTHER_ENV_VARS,),
    )
    @unpack
    def test_normal_construction(self, env_vars):
        mock_os = patch.dict('helpers.environment.os.environ', env_vars)
        mock_os.start()

        test_env = environment.Environment()
        self.mock_yaml.safe_load.assert_called_once()
        self.assertEqual(test_env.mongodb_uri, env_vars['MONGODB_URI'])
        self.assertEqual(test_env.db_name, 'Match')
        self.assertEqual(test_env.environment, env_vars['ENVIRONMENT'])

        env_type = env_vars['ENVIRONMENT']
        self.assertEqual(test_env.property1, TEST_YAML_DATA[env_type]['property1'])
        self.assertEqual(test_env.property2, TEST_YAML_DATA[env_type]['property2'])
        self.assertEqual(test_env.property_int, TEST_YAML_DATA[env_type]['property_int'])

        mock_os.stop()

    def test_single_yaml_load(self):
        """
        The Environment class is implemented according to the Singleton pattern.
        Test that it is only created once.
        """
        environment.Environment()
        environment.Environment()
        environment.Environment()
        self.mock_yaml.safe_load.assert_called_once()

    @patch('helpers.environment.exit')
    def test_missing_env_var(self, mock_exit):
        # Mock what happens when a required environment variable is missing
        self.mock_os.environ = MagicMock()
        self.mock_os.environ.__getitem__.side_effect = KeyError('ENVIRONMENT')

        with self.assertRaises(KeyError) as cm:
            environment.Environment()
            self.mock_logger.error.assert_called_with(environment.Environment.REQ_VARS_MSG)

        self.mock_logger.error.assert_called_with(str(cm.exception))
        self.assertIn('exit', repr(mock_exit))

    def test_invalid_get(self):
        with self.assertRaises(Exception) as cm:
            test_env = environment.Environment()
            # Environment has no 'invalid_get' member, so causes exception.
            # Must disable pylint warning about "Statement seems to have no effect."
            test_env.invalid_get  # pylint: disable=pointless-statement
        exp_exc_msg = environment.Environment.INVALID_GET_MSG_FMT.format('invalid_get')
        self.assertEqual(str(cm.exception), exp_exc_msg)

    def test_load_config_file_with_exc(self):
        self.mock_open.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError) as cm:
            environment.Environment()
        self.assertIn(environment.Environment.MISSING_CONFIG_FILE_MSG, str(cm.exception))
        self.mock_logger.exception.assert_called_once()

if __name__ == '__main__':
    unittest.main()
