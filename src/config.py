import os

class AppConfig:
    APP_NAME="cfn-docgen"
    APP_ROOT_DIR=os.path.join(
        os.path.expanduser("~"), f".{APP_NAME}"
    )
    DEFAULT_SPECIFICATION_URL="https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"