# import base64
import os
from functools import wraps

import jwt
from flask import request, jsonify, _request_ctx_stack
from flask_restful import Resource
from werkzeug.local import LocalProxy

# from helpers.environment import Environment

# Authentication annotation
current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)


def error_response(code, description):  # pragma: no cover
    response = jsonify({'code': code, 'description': description})
    response.status_code = 401
    return response


def requires_auth(function):  # pragma: no cover
    # if Environment().environment == 'development':
        # print("************ returning function without authorization ************")
    if 'UNITTEST' in os.environ:
        # print("************ returning function without authorization ************")
        return function
    else:
        @wraps(function)
        def decorated(*args, **kwargs):
            # print("************ authorizing ************")
            auth = request.headers.get('Authorization', None)
            # print(str(auth))
            if not auth:
                return error_response('authorization_header_missing', 'Authorization header is expected')

            parts = auth.split()

            if parts[0].lower() != 'bearer':
                return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
            elif len(parts) == 1:
                return {'code': 'invalid_header', 'description': 'Token not found'}
            elif len(parts) > 2:
                return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}
            token = parts[1]

            try:
                auth0_client_secret = os.environ['AUTH0_CLIENT_SECRET']
            except KeyError:
                return error_response('missing secret', 'Environment variable AUTH0_CLIENT_SECRET is missing')

            # auth0_client_secret = auth0_client_secret if len(auth0_client_secret) == 64 else  base64.b64decode(
            #     auth0_client_secret)

            try:
                auth0_client_id = os.environ['AUTH0_CLIENT_ID']
            except KeyError:
                return error_response('missing client ID', 'Environment variable AUTH0_CLIENT_ID is missing')

            try:
                payload = jwt.decode(token, auth0_client_secret, audience=auth0_client_id)
            except jwt.ExpiredSignature:
                return error_response('token_expired', 'token is expired')
            except jwt.InvalidAudienceError:
                return error_response('invalid_audience', 'incorrect audience')
            except jwt.DecodeError:
                return error_response('token_invalid_signature', 'token signature is invalid')
            except Exception as e:
                return error_response('Unknown_exception_raised', str(e))

            # Check for proper parameters in token.
            if 'roles' not in payload or 'email' not in payload:
                return error_response('token_incomplete', 'token must contain roles and email in scope!')

            # print("Executing function")
            return function(*args, **kwargs)

        return decorated


class Auth0Resource(Resource):  # pragma: no cover
    method_decorators = [requires_auth]
