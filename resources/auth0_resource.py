"""
Implements Auth0 authentication.
"""
# import base64
import os
from functools import wraps

import jwt
import requests
from flask import request, jsonify, _request_ctx_stack
from flask_restful import Resource
from werkzeug.local import LocalProxy


# Authentication annotation
current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)

AUTH_URI = "https://ncimatch.auth0.com/oauth/ro"


def requires_auth(function):
    if 'UNITTEST' in os.environ:
        # print("************ returning function {} without authorization ************".format(function.__name__))
        return function
    else:
        # print("************ returning function {} with authorization ************".format(function.__name__))
        return authenticated_function(function)


class AuthenticationError(Exception):
    def __init__(self, code, description):
        self.code = code
        self.description = description


def error_response(code, description):
    response = jsonify({'code': code, 'description': description})
    response.status_code = 401
    return response


def authenticated_function(function):
    """
    Decorates function with Auth0 authentication.
    :param function: a function that requires authentication in order to execute.
    :return: the function decorated with authentication logic
    """
    @wraps(function)
    def decorated(*args, **kwargs):
        # print("Authenticating for {}".format(function.__name__))
        try:
            authenticate()

        except AuthenticationError as e:
            print("authentication error: {} / }|".format(e.code, e.description))
            return error_response(e.code, e.description)

        # print("Executing function")
        return function(*args, **kwargs)

    return decorated


def authenticate():
    # print("in authenticate")
    token = get_authentication_token()

    # print("token={}".format(token))
    auth0_client_id = read_environment_variable('AUTH0_CLIENT_ID')
    auth0_client_secret = read_environment_variable('AUTH0_CLIENT_SECRET')

    # auth0_client_secret = auth0_client_secret if len(auth0_client_secret) == 64 else  base64.b64decode(
    # auth0_client_secret)

    validate_token(token, auth0_client_id, auth0_client_secret)


def read_environment_variable(env_var):
    # print("in read_environment_variable with '{}'".format(env_var))
    try:
        auth0_client_id = os.environ[env_var]
    except KeyError:
        raise AuthenticationError('missing_env_var', 'Required environment variable {} is missing'.format(env_var))
    return auth0_client_id


def get_authentication_token():
    """
    Obtains the authorization header and returns the token if the header is formatted correctly.  Otherwise,
    :return: the authentication token string
    :raises AuthenticationError if the authorization header is not formatted correctly.
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthenticationError('authorization_header_missing', 'Authorization header is expected')
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthenticationError('invalid_header', 'Authorization header must start with Bearer')
    elif len(parts) == 1:
        raise AuthenticationError('invalid_header', 'Token not found')
    elif len(parts) > 2:
        raise AuthenticationError('invalid_header', 'Authorization header must be Bearer + \s + token')
    token = parts[1]
    return token


def validate_token(token, auth0_client_id, auth0_client_secret):
    """
    Validates the token with the client ID and secret.
    :param token: the user's authentication token
    :param auth0_client_id: the client ID
    :param auth0_client_secret: the client secret
    :raises AuthenticationError if the token can not be decoded or is missing one of the following: 'roles', 'email'
    """
    # print("in validate_token")
    try:
        payload = jwt.decode(token, auth0_client_secret, audience=auth0_client_id)

    # Note: Exception handling is currently exempt from coverage because there is a python bug that results in the
    # the following error when a unit test is tried:
    #   "TypeError: catching classes that do not inherit from BaseException is not allowed"
    # That error makes no sense as all five of these exception classes inherit from BaseException.
    except jwt.ExpiredSignatureError:  # pragma: no cover
        # print("ExpiredSignatureError")
        raise AuthenticationError('token_expired', 'token is expired')
    except jwt.InvalidAudienceError:  # pragma: no cover
        # print("InvalidAudienceError")
        raise AuthenticationError('invalid_audience', 'incorrect audience')
    except jwt.DecodeError:  # pragma: no cover
        # print("DecodeError")
        raise AuthenticationError('token_invalid_signature', 'token signature is invalid')
    # Catch base exceptions
    except jwt.InvalidTokenError:  # pragma: no cover
        # print("InvalidTokenError")
        raise AuthenticationError('invalid_token', 'token is invalid')
    except Exception as e:  # pragma: no cover
        # print(str(e))
        raise AuthenticationError('unknown_exception_raised', str(e))

    # Check for proper parameters in token.
    if 'roles' not in payload or 'email' not in payload:
        raise AuthenticationError('token_incomplete', 'token must contain roles and email in scope!')


class Auth0Resource(Resource):  # pragma: no cover
    method_decorators = [requires_auth]


def create_authentication_token():
    auth0_client_id = read_environment_variable('AUTH0_CLIENT_ID')
    auth0_client_database = read_environment_variable('AUTH0_DATABASE')
    auth0_username = read_environment_variable('AUTH0_USERNAME')
    auth0_password = read_environment_variable('AUTH0_PASSWORD')

    body = {
        "client_id": auth0_client_id,
        "connection": auth0_client_database,
        "username": auth0_username,
        "password": auth0_password,
        "grant_type": "password",
        "scope": "openid roles email",
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(AUTH_URI, headers=headers, json=body)
    response_data = response.json()

    if 'error' in response_data:
        raise AuthenticationError(response_data['error'], response_data['error_description'])
    elif 'id_token' not in response_data:
        raise AuthenticationError("unexpected_response", "'id_token' not found in response")

    return "bearer " + response_data['id_token']
