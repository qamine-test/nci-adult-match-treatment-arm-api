"""
Logging configuration
"""

import logging.config

study_id = 'EAY131'

def log_config():
    """
    Configures logging globally
    """
    LOGGER_CONFIGURATION = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(levelname)s - TREATMENT_ARM_API ['+study_id+'] - %(name)s.%(module)s.%(funcName)s:%(lineno)d - %(message)s',
            },
        },
        'handlers': {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level':'DEBUG',
            }
        }
    }

    logging.config.dictConfig(LOGGER_CONFIGURATION)
