from __future__ import annotations
from dataclasses import dataclass
from logging import Logger
import logging
import os
from typing import List, Optional
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
class AppContextLogMessages:
    info: List[str]
    warning: List[str]
    error: List[str]
    debug: List[str]

    def as_string(self, level:int, delimiter:str="\n") -> str:
        prefix = ""
        messages:List[str] = []
        match level:
            case logging.INFO:
                prefix = "INFO"
                messages = self.info
            case logging.WARNING:
                prefix = "WARNING"
                messages = self.warning
            case logging.ERROR:
                prefix = "ERROR"
                messages = self.error
            case logging.DEBUG:
                prefix = "DEBUG"
                messages = self.debug
            case _:
                return ""
            
        return delimiter.join([f"[{prefix}] {message}" for message in messages])

class AppContext:

    def __init__(
        self, 
        request_id:Optional[str]=None,
        logger_name:str="cfn-docgen", 
        log_level:int=logging.CRITICAL, 
    ) -> None:
        self.request_id = str(uuid.uuid4()) if request_id is None else request_id
        self.__logger = AppLogger(name=logger_name, loglevel=log_level, stacklevel=3)
        self.log_messages = AppContextLogMessages(
            info=[], warning=[], error=[], debug=[],
        )
    def log_info(self, msg:str, ):
        self.log_messages.info.append(msg)
        self.__logger.info(msg)
    def log_warning(self, msg:str):
        self.log_messages.warning.append(msg)
        self.__logger.warning(msg)
    def log_error(self, msg:str):
        self.log_messages.error.append(msg)
        self.__logger.error(msg)
    def log_debug(self, msg:str):
        self.log_messages.debug.append(msg)
        self.__logger.debug(msg)

class AppLogger:
    __logger: Logger
    def __init__(self, name:str, loglevel:int, stacklevel:int) -> None:
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(loglevel)

        self.__logger = logger
        self.__stacklevel = stacklevel

    def info(self, msg:str, ):
        self.__logger.info(msg, stacklevel=self.__stacklevel)
    def warning(self, msg:str):
        self.__logger.warning(msg, stacklevel=self.__stacklevel)
    def error(self, msg:str):
        self.__logger.error(msg, stacklevel=self.__stacklevel, exc_info=True)
    def debug(self, msg:str):
        self.__logger.debug(msg, stacklevel=self.__stacklevel)