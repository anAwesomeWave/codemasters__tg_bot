import os
import logging
from logging.handlers import RotatingFileHandler

from settings import BASE_DIR

LOG_DIR = BASE_DIR + 'logs/'

"""Модуль для настройки логгера проекта."""


def create_logger(name, filename):
    logger = logging.getLogger(name)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    handler = RotatingFileHandler(
        LOG_DIR + filename, maxBytes=10000, backupCount=1
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
