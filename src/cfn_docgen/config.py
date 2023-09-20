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
    SPECIFICATION_URL_BY_REGION = {
        "us-east-2": "https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-east-1": "https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-west-1": "https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-west-2": "https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "af-south-1": "https://cfn-resource-specifications-af-south-1-prod.s3.af-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-east-1": "https://cfn-resource-specifications-ap-east-1-prod.s3.ap-east-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-south-2": "https://cfn-resource-specifications-ap-south-2-prod.s3.ap-south-2.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-southeast-3": "https://cfn-resource-specifications-ap-southeast-3-prod.s3.ap-southeast-3.amazonaws.com/latest/CloudFormationResourceSpecification.json",
        "ap-southeast-4": "https://cfn-resource-specifications-ap-southeast-4-prod.s3.ap-southeast-4.amazonaws.com/latest/CloudFormationResourceSpecification.json",
        "ap-south-1": "https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-northeast-3": "https://d2zq80gdmjim8k.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-northeast-2": "https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-southeast-1": "https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-southeast-2": "https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-northeast-1": "https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ca-central-1": "https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        # "cn-north-1": "https://cfn-resource-specifications-cn-north-1-prod.s3.cn-north-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json",
        # "cn-northwest-1": "https://cfn-resource-specifications-cn-northwest-1-prod.s3.cn-northwest-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-central-1": "https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-west-1": "https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-west-2": "https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-south-1": "https://cfn-resource-specifications-eu-south-1-prod.s3.eu-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-west-3": "https://d2d0mfegowb3wk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-south-2": "https://cfn-resource-specifications-eu-south-2-prod.s3.eu-south-2.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-north-1": "https://diy8iv58sj6ba.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-central-2": "https://cfn-resource-specifications-eu-central-2-prod.s3.eu-central-2.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "il-central-1": "https://cfn-resource-specifications-il-central-1-prod.s3.il-central-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "me-south-1": "https://cfn-resource-specifications-me-south-1-prod.s3.me-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "me-central-1": "https://cfn-resource-specifications-me-central-1-prod.s3.me-central-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "sa-east-1": "https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-gov-east-1": "https://s3.us-gov-east-1.amazonaws.com/cfn-resource-specifications-us-gov-east-1-prod/latest/CloudFormationResourceSpecification.json",
        "us-gov-west-1": "https://s3.us-gov-west-1.amazonaws.com/cfn-resource-specifications-us-gov-west-1-prod/latest/CloudFormationResourceSpecification.json",
    }
    RECURSIVE_RESOURCE_TYPES=[
        "AWS::WAFv2::WebACL",
        "AWS::WAFv2::RuleGroup",
        "AWS::AmplifyUIBuilder::Component",
        "AWS::IoTTwinMaker::Entity",
        "AWS::IoTTwinMaker::ComponentType",
        "AWS::EMR::Cluster",
        "AWS::EMR::InstanceFleetConfig",
        "AWS::EMR::InstanceGroupConfig",
        "AWS::AmplifyUIBuilder::Theme",
        "AWS::Connect::EvaluationForm",
        "AWS::Lex::Bot",
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