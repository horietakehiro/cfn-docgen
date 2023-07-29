import logging
from pythonjsonlogger import jsonlogger
from src.domain.ports.logger import ILogger

class JsonStreamLogger(ILogger):

    def __init__(self, name: str, level: int) -> None:
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)
        self.__loghandler = logging.StreamHandler()
        self.__formatter = jsonlogger.JsonFormatter()
        self.__loghandler.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__loghandler)

    def info(self, msg: str):
        self.__logger.info(msg)
    def warning(self, msg: str):
        self.__logger.warning(msg)
    def error(self, msg: str):
        self.__logger.error(msg)
    def debug(self, msg: str):
        self.__logger.debug(msg)

