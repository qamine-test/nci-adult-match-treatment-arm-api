"""
Logging configuration
"""

import logging.config

PREFIX = 'NciAdultMatchTreatmentArmApi'


def log_config(logger_level="DEBUG"):
    """Configure logging globally."""
    logger_configuration = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s {prefix} %(levelname)s %(name)s.%(module)s.%(funcName)s:'
                          '%(lineno)d - %(message)s'.format(prefix=PREFIX),
            },
        },
        'handlers': {
            "console": {
                "class": "logging.StreamHandler",
                "level": logger_level,
                # "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': logger_level,
            }
        }
    }

    logging.config.dictConfig(logger_configuration)
