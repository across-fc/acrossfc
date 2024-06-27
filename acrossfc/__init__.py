# stdlib
import os
import logging
import logging.config

# Local
from .utils import setup_utils

# Configure root logger
ROOT_LOGGER_NAME = 'acrossfc'
LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d: %(message)s"
)
ANALYTICS_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)s] AX_ANALYTICS: %(message)s"
)

log_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': LOG_FORMAT
        },
        'analytics': {
            'format': ANALYTICS_LOG_FORMAT
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'analytics': {
            'class': 'logging.StreamHandler',
            'formatter': 'analytics',
        },
    },
    'loggers': {
        ROOT_LOGGER_NAME: {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False
        },
        'AX_ANALYTICS': {
            'level': 'INFO',
            'handlers': ['analytics'],
            'propagate': False
        },
    },
}

logging.config.dictConfig(log_config)
ROOT_LOG = logging.getLogger(ROOT_LOGGER_NAME)
ANALYTICS_LOG = logging.getLogger('AX_ANALYTICS')

ENV = os.environ.get('AX_ENV', 'TEST')

# Setup util functions and such
setup_utils()
