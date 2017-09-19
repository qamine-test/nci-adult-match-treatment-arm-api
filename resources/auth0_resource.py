import jwt
import os
import base64

from functools import wraps
from flask_restful import Resource
from flask import request, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy

from helpers.environment import Environment

# Authentication annotation
current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)


# Authentication attribute/annotation
def authenticate(error):  # pragma: no cover
    response = jsonify(error)
    response.status_code = 401
    return response


def requires_auth(function):  # pragma: no cover
    # try:
    #     os.environ['UNITTEST']
    #     return function
    # except Exception:
    if Environment().environment == 'development':
        print("************ returning function without authorization ************")
        return function
    else:
        @wraps(function)
        def decorated(*args, **kwargs):
            print("************ authorizing ************")
            auth = request.headers.get('Authorization', None)
            print(str(auth))
            if not auth:
                return authenticate(
                    {'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

            parts = auth.split()

            if parts[0].lower() != 'bearer':
                return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
            elif len(parts) == 1:
                return {'code': 'invalid_header', 'description': 'Token not found'}
            elif len(parts) > 2:
                return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}
            token = parts[1]
            # auth0_client_secret = base64.b64decode(
            #     os.environ['AUTH0_CLIENT_SECRET'].replace("_", "/").replace("-", "+"))
            auth0_client_secret = os.environ['AUTH0_CLIENT_SECRET']
            auth0_client_secret = auth0_client_secret if len(auth0_client_secret) == 64 else  base64.b64decode(
                auth0_client_secret)
            auth0_client_id = os.environ['AUTH0_CLIENT_ID']
            try:
                payload = jwt.decode(token, auth0_client_secret, audience=auth0_client_id)
            except jwt.ExpiredSignature:
                return authenticate({'code': 'token_expired', 'description': 'token is expired'})
            except jwt.InvalidAudienceError:
                return authenticate(
                    {'code': 'invalid_audience', 'description': 'incorrect audience, expected: '})
            except jwt.DecodeError:
                return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})
            # Check for proper parameters in token.
            try:
                payload['roles']
            except KeyError:
                return authenticate(
                    {'code': 'token_incomplete', 'description': 'token must contain roles and email in scope!'})
            try:
                payload['email']
            except KeyError:
                return authenticate(
                    {'code': 'token_incomplete', 'description': 'token must contain roles and email in scope!'})

            return function(*args, **kwargs)

        return decorated


class Auth0Resource(Resource):  # pragma: no cover
    method_decorators = [requires_auth]
