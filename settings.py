#! python3
# -*- coding: utf-8 -*-

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        }
    },
    'handlers': {
        'file': {"level": "INFO", "class": "logging.StreamHandler", "formatter": "standard"}
    },
    'loggers': {
        'client': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'unittest_logger': {
            'handlers': ['file'],
            'level': 'INFO'
        }
    }
}