"""
Logging configuration
"""

import logging.config

# study_id = 'EAY131'
PREFIX = 'NciAdultMatchTreatmentArmApi'


def log_config():
    """Configure logging globally."""
    logger_configuration = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s {prefix} %(levelname)s %(name)s.%(module)s.%(funcName)s:'
                          '%(lineno)d - %(message)s'.format(prefix=PREFIX),
                # 'format': '%(asctime)s - %(levelname)s - {prefix} [{study_id}] - %(name)s.%(module)s.%(funcName)s:'
                #           '%(lineno)d - %(message)s'.format(prefix=PREFIX, study_id=STUDY_ID),
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
                'level': 'DEBUG',
            }
        }
    }

    logging.config.dictConfig(logger_configuration)
