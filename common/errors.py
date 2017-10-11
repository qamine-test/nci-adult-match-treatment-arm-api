"""
Application error handlers.
"""

import logging
from flask import Blueprint, jsonify

ERRORS = Blueprint('errors', __name__)
LOGGER = logging.getLogger(__name__)


@ERRORS.app_errorhandler(Exception)
def handle_unexpected_error(error):
    """
    Handler for a generic server error
    """
    status_code = 500
    success = False
    response = {
        'success': success,
        'error': {
            'type': 'UnexpectedException',
            'message': str(error)
        }
    }

    LOGGER.exception(str(error))

    return jsonify(response), status_code
