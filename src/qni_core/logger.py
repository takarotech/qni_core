import logging

LOGGING_LEVEL = logging.INFO
LOGGING_FORMATS = {
    'format': '%(asctime)s %(name)s %(levelname)s: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}


def config_logger():
	logging.basicConfig(level=LOGGING_LEVEL, **LOGGING_FORMATS)
