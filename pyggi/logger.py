import logging
import time

class Logger(object):
    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s]\t%(message)s')
        fileHandler = logging.FileHandler("{}_{}.log".format(name, int(time.time())))
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logging.INFO)
        self._logger.addHandler(fileHandler)
        self._logger.addHandler(streamHandler)
    
    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)

    def critical(self, msg):
        self._logger.critical(msg)

