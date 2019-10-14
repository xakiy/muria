"""Logging."""

import logging


class Logger(object):
    def __init__(self, config):
        self.config = config

    def getLogger(self):
        logger = logging.getLogger(self.config.get("app", "logger_name"))
        logger.setLevel(self.config.getint("app", "logger_level"))
        logger.propogate = False
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        return logger
