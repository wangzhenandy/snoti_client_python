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
        'file': {"level": "INFO", "class": "logging.StreamHandler", "formatter": "standard"},
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'mytest.log',
            'maxBytes': 64*1024*1024,
            'backupCount': 10,
            'formatter': 'standard',
        }
    },
    'loggers': {
        'client': {
            'handlers': ['logfile'],
            'level': 'INFO'
        },
        'unittest_logger': {
            'handlers': ['file'],
            'level': 'INFO'
        }
    }
}