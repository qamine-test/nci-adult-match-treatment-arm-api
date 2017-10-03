"""
Logging configuration
"""

import logging.config

study_id = 'EAY131'
prefix = 'NciAdultMatchTreatmentArmApi'

def log_config():
    """
    Configures logging globally
    """
    LOGGER_CONFIGURATION = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(levelname)s - {prefix} [{study_id}] - %(name)s.%(module)s.%(funcName)s:'
                          '%(lineno)d - %(message)s'.format(prefix=prefix, study_id=study_id),
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
