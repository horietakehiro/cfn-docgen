from __future__ import annotations
from dataclasses import dataclass
import datetime
from logging import Logger
import logging
import os
from typing import Iterable, List, Optional
import uuid

class AppConfig:
    APP_NAME="cfn-docgen"
    APP_ROOT_DIR=os.path.join(
        os.path.expanduser("~"), f".{APP_NAME}"
    )
    CACHE_ROOT_DIR=os.path.join(APP_ROOT_DIR, "cache")
    DEFAULT_SPECIFICATION_URL="https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"
    RECURSIVE_RESOURCE_TYPES=[
        "AWS::WAFv2::WebACL",
        "AWS::WAFv2::RuleGroup",
        "AWS::AmplifyUIBuilder::Component",
        "AWS::IoTTwinMaker::ComponentType",
    ]

@dataclass
class AppContextLogMessage:
    level: int
    message: str
    timestamp: float
@dataclass
class AppContextLogMessages:
    messages: List[AppContextLogMessage]

    def as_string(self, level:int, delimeter:str="\n") -> str:
        prefixes = {
            logging.INFO: "[INFO]",
            logging.WARNING: "[WARNING]",
            logging.ERROR: "[ERROR]",
            logging.DEBUG: "[DEBUG]",
        }
        return_messages:Iterable[str] = map(
            lambda m: f"{prefixes[m.level]} {m.message}",
            filter(
                lambda m: m.level >= level, 
                sorted(self.messages, key=lambda m: m.timestamp),
            )
        )
        return delimeter.join(return_messages)

@dataclass
class AwsConnectionSettings:
    profile_name:Optional[str]

@dataclass
class ConnectionSettings:
    aws: AwsConnectionSettings

class AppContext:

    def __init__(
        self, 
        request_id:Optional[str]=None,
        logger_name:str="cfn-docgen", 
        log_level:int=logging.CRITICAL,
        connection_settings:Optional[ConnectionSettings]=None,
    ) -> None:        
        self.request_id = str(uuid.uuid4()) if request_id is None else request_id
        self.__logger = AppLogger(name=logger_name, loglevel=log_level, stacklevel=3)
        self.log_messages = AppContextLogMessages(messages=[])
        self.connection_settings = connection_settings

    def log_info(self, msg:str, ):
        now = datetime.datetime.now().timestamp()
        self.log_messages.messages.append(AppContextLogMessage(
            level=logging.INFO, message=msg, timestamp=now,
        ))
        self.__logger.info(msg)

    def log_warning(self, msg:str):
        now = datetime.datetime.now().timestamp()
        self.log_messages.messages.append(AppContextLogMessage(
            level=logging.WARNING, message=msg, timestamp=now,
        ))
        self.__logger.warning(msg)

    def log_error(self, msg:str):
        now = datetime.datetime.now().timestamp()
        self.log_messages.messages.append(AppContextLogMessage(
            level=logging.ERROR, message=msg, timestamp=now,
        ))
        self.__logger.error(msg)

    def log_debug(self, msg:str):
        now = datetime.datetime.now().timestamp()
        self.log_messages.messages.append(AppContextLogMessage(
            level=logging.DEBUG, message=msg, timestamp=now,
        ))
        self.__logger.debug(msg)

class AppLogger:
    __logger: Logger
    def __init__(self, name:str, loglevel:int, stacklevel:int) -> None:
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(loglevel)

        self.__logger = logger
        self.__stacklevel = stacklevel

    def info(self, msg:str, ):
        self.__logger.info(msg, stacklevel=self.__stacklevel)
    def warning(self, msg:str):
        self.__logger.warning(msg, stacklevel=self.__stacklevel, exc_info=True)
    def error(self, msg:str):
        self.__logger.error(msg, stacklevel=self.__stacklevel, exc_info=True)
    def debug(self, msg:str):
        self.__logger.debug(msg, stacklevel=self.__stacklevel)