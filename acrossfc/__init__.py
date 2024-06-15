import logging
import logging.config

ROOT_LOGGER_NAME = 'acrossfc'
LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d: %(message)s"
)

log_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': LOG_FORMAT
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        ROOT_LOGGER_NAME: {
            'level': 'INFO',
            'handlers': ['console']
        },
    },
}

if len(logging.getLogger().handlers) == 0:
    logging.config.dictConfig(log_config)
    root_logger = logging.getLogger(ROOT_LOGGER_NAME)
else:
    root_logger = logging.getLogger()
