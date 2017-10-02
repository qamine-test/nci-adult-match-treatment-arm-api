#!/usr/bin/env python3

import unittest

import flask
from ddt import ddt, data, unpack
from mock import patch, Mock

# import jwt
from resources import auth0_resource


def test_function():
    return 2 + 2


@ddt
class Auth0ResourceTests(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)

    # Test the auth0_resource.requires_auth function
    @data(
        ({'UNITTEST': 1}, True),
        ({}, False),
    )
    @unpack
    def test_requires_auth(self, mock_os_environ, is_same_function):
        with patch('resources.auth0_resource.os') as mock_os:
            mock_os.environ = mock_os_environ
            function = auth0_resource.requires_auth(test_function)
            if is_same_function:
                self.assertEqual(function, test_function)
            else:
                self.assertNotEqual(function, test_function)

    # Test the auth0_resource.error_response function
    def test_error_response(self):
        test_code = 'my_test_code'
        test_description = 'this describes what went wrong'

        with self.app.test_request_context():
            exp_data = {'code': test_code, 'description': test_description}

            response = auth0_resource.error_response(test_code, test_description)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(flask.json.loads(response.data.decode("utf-8")), exp_data)

    # Test the auth0_resource.get_authentication_token function
    @data(
        # 1.  Everything is correct.
        ({'Authorization': 'Bearer MyTestToken'}, 'MyTestToken'),
        # 2.  Exception for too many things in the Authorization header
        ({'Authorization': 'bearer MyTestToken OtherStuff'},
         auth0_resource.AuthenticationError('invalid_header', 'Authorization header must be Bearer + \s + token')),
        # 3.  Exception for too few things in the Authorization header
        ({'Authorization': 'bearer'},
         auth0_resource.AuthenticationError('invalid_header', 'Token not found')),
        # 4.  Exception for improper format of Authorization header: does not start with 'bearer'
        ({'Authorization': 'MyTestToken OtherStuff'},
         auth0_resource.AuthenticationError('invalid_header', 'Authorization header must start with Bearer')),
        # 5.  Exception for missing Authorization header
        ({'Authorin': 'Bearer MyTestToken'},
         auth0_resource.AuthenticationError('authorization_header_missing', 'Authorization header is expected')),
    )
    @unpack
    @patch('resources.auth0_resource.request')
    def test_get_authentication_token(self, headers, exp_result, mock_request):
        mock_request.headers = headers

        if isinstance(exp_result, Exception):
            with self.assertRaises(auth0_resource.AuthenticationError) as cm:
                auth0_resource.get_authentication_token()
            self.assertEqual(str(cm.exception), str(exp_result))
        else:
            result = auth0_resource.get_authentication_token()
            self.assertEqual(result, exp_result)

    # Test the auth0_resource.validate_token function
    @data(
        # 1.  Everything is correct.
        ([{'roles': 1, 'email': '1@a.com'}], None),
        # 2.  Exception for missing email
        ([{'roles': 1}],
         auth0_resource.AuthenticationError('token_incomplete', 'token must contain roles and email in scope!')),
        # 3.  Exception for missing roles
        ([{'email': '1@a.com'}],
         auth0_resource.AuthenticationError('token_incomplete', 'token must contain roles and email in scope!')),

        # Note: Exception handling is currently exempt from coverage because there is a python bug that results in the
        # the following error when these unit test cases are tried:
        #   "TypeError: catching classes that do not inherit from BaseException is not allowed"
        # That error makes no sense as all five of these exception classes inherit from BaseException.
        #
        # # 4.  jwt raises ExpiredSignatureError exception
        # (jwt.ExpiredSignatureError('error'),
        #  auth0_resource.AuthenticationError('token_expired', 'token is expired')),
        # # 5.  jwt raises InvalidAudienceError exception
        # (jwt.InvalidAudienceError('error'),
        #  auth0_resource.AuthenticationError('invalid_audience', 'incorrect audience')),
        # # 6.  jwt raises DecodeError exception
        # (jwt.DecodeError('error'),
        #  auth0_resource.AuthenticationError('token_invalid_signature', 'token signature is invalid')),
        # # 7.  jwt raises InvalidTokenError exception (base jwt exception class)
        # (jwt.InvalidTokenError('error'),
        #  auth0_resource.AuthenticationError('token_invalid_signature', 'token signature is invalid')),
        # # 8.  jwt raises unknown exception
        # (Exception('error'),
        #  auth0_resource.AuthenticationError('unknown_exception_raised', 'error')),
    )
    @unpack
    @patch('resources.auth0_resource.jwt')
    def test_validate_token(self, decode_result, exp_result, mock_jwt):
        mock_jwt.decode = Mock(side_effect=decode_result)

        auth_token = 'MyTestToken'
        client_id = 'MyClientId'
        client_secret = 'MyClientSecret'

        if isinstance(exp_result, Exception):
            with self.assertRaises(auth0_resource.AuthenticationError) as cm:
                auth0_resource.validate_token(auth_token, client_id, client_secret)
            self.assertEqual(str(cm.exception), str(exp_result))
        else:
            auth0_resource.validate_token(auth_token, client_id, client_secret)
            mock_jwt.decode.assert_called_once_with(auth_token, client_secret, audience=client_id)

    # Test the auth0_resource.authenticate function
    @data(
        # 1.  Everything is correct.
        ({'AUTH0_CLIENT_ID': 'MyClientId', 'AUTH0_CLIENT_SECRET': 'MyClientSecret'},
         'MyTestToken', None),
        # 2.  Environment is missing AUTH0_CLIENT_ID env var
        ({'AUTH0_CLIENT_SECRET': 'MyClientSecret'}, 'MyTestToken',
         auth0_resource.AuthenticationError('missing_env_var',
                                            'Required environment variable AUTH0_CLIENT_ID is missing')),
        # 3.  Environment is missing AUTH0_CLIENT_SECRET env var
        ({'AUTH0_CLIENT_ID': 'MyClientId'}, 'MyTestToken',
         auth0_resource.AuthenticationError('missing_env_var',
                                            'Required environment variable AUTH0_CLIENT_SECRET is missing')),
        # 4.  get_authentication_token throws an exception
        ({'AUTH0_CLIENT_ID': 'MyClientId'},
         auth0_resource.AuthenticationError('invalid_header', 'Token not found'),
         auth0_resource.AuthenticationError('invalid_header', 'Token not found')),
    )
    @unpack
    @patch('resources.auth0_resource.validate_token')
    @patch('resources.auth0_resource.get_authentication_token')
    @patch('resources.auth0_resource.os')
    def test_authenticate(self, mock_env_vars, token_result, exp_result, mock_os, mock_get_authentication_token,
                          mock_validate_token):
        mock_os.environ = mock_env_vars
        mock_get_authentication_token.side_effect = [token_result]

        if isinstance(exp_result, Exception):
            with self.assertRaises(auth0_resource.AuthenticationError) as cm:
                auth0_resource.authenticate()
            self.assertEqual(str(cm.exception), str(exp_result))
            mock_validate_token.assert_not_called()
        else:
            auth0_resource.authenticate()
            mock_validate_token.assert_called_once_with(token_result, mock_env_vars['AUTH0_CLIENT_ID'],
                                                        mock_env_vars['AUTH0_CLIENT_SECRET'])


    # Test the auth0_resource.authenticated_function function when authentication occurs
    @patch('resources.auth0_resource.authenticate')
    def test_authenticated_function(self, mock_authenticate):
        decorated_function = auth0_resource.authenticated_function(test_function)

        exp_result = test_function()
        result = decorated_function()
        self.assertEqual(result, exp_result)
        mock_authenticate.assert_called_once_with()

    # Test the auth0_resource.authenticated_function function when authentication does not occur
    @patch('resources.auth0_resource.authenticate')
    def test_authenticated_function_cannot_authenticate(self, mock_authenticate):
        test_exception = auth0_resource.AuthenticationError('test_code', 'my test exception description')
        mock_authenticate.side_effect = test_exception  # exception indicates that the user could not be authenticated.

        decorated_function = auth0_resource.authenticated_function(test_function)

        exp_data = {'code': test_exception.code, 'description': test_exception.description}

        with self.app.test_request_context():
            response = decorated_function()
            self.assertEqual(response.status_code, 401)
            self.assertEqual(flask.json.loads(response.data.decode("utf-8")), exp_data)
        mock_authenticate.assert_called_once_with()

    # Test the auth0_resource.create_authentication_token function
    @data(
        # 1.  Everything is correct.
        ({'AUTH0_CLIENT_ID': 'id', 'AUTH0_DATABASE': 'db', 'AUTH0_USERNAME': 'un', 'AUTH0_PASSWORD': 'pw'},
         {'id_token': 'my_made_up_id_token'},
         "bearer my_made_up_id_token"),
        # 2.  Completely unexpected response
        ({'AUTH0_CLIENT_ID': 'id', 'AUTH0_DATABASE': 'db', 'AUTH0_USERNAME': 'un', 'AUTH0_PASSWORD': 'pw'},
         {'unexpected': 'response'},
         auth0_resource.AuthenticationError("unexpected_response", "'id_token' not found in response")),
        # 3.  Error response indicates what went wrong
        ({'AUTH0_CLIENT_ID': 'id', 'AUTH0_DATABASE': 'db', 'AUTH0_USERNAME': 'un', 'AUTH0_PASSWORD': 'pw'},
         {'error': 'invalid_token', 'error_description': 'The token is not valid'},
         auth0_resource.AuthenticationError("invalid_token", "The token is not valid")),
        # 4.  Environment is missing AUTH0_CLIENT_ID env var
        ({'AUTH0_DATABASE': 'db', 'AUTH0_USERNAME': 'un', 'AUTH0_PASSWORD': 'pw'},
         {'error': 'invalid_token', 'error_description': 'The token is not valid'},
         auth0_resource.AuthenticationError('missing_env_var',
                                            'Required environment variable AUTH0_CLIENT_ID is missing')),
    )
    @unpack
    @patch('resources.auth0_resource.os')
    @patch('resources.auth0_resource.requests')
    def test_create_authentication_token(self, mock_env_vars, response_data, exp_result, mock_requests, mock_os):
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_requests.post.return_value = mock_response
        mock_os.environ = mock_env_vars

        if isinstance(exp_result, Exception):
            with self.assertRaises(auth0_resource.AuthenticationError) as cm:
                auth0_resource.create_authentication_token()
            self.assertEqual(str(cm.exception), str(exp_result))
        else:
            result = auth0_resource.create_authentication_token()
            self.assertEqual(result, exp_result)
            mock_requests.post.assert_called_once_with(auth0_resource.AUTH_URI,
                                                       headers={"Content-Type": "application/json"},
                                                       json={
                                                           "client_id": mock_env_vars['AUTH0_CLIENT_ID'],
                                                           "connection": mock_env_vars['AUTH0_DATABASE'],
                                                           "username": mock_env_vars['AUTH0_USERNAME'],
                                                           "password": mock_env_vars['AUTH0_PASSWORD'],
                                                           "grant_type": "password",
                                                           "scope": "openid roles email",
                                                       })

if __name__ == '__main__':
    unittest.main()
