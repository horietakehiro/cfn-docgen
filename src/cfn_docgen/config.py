import os

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