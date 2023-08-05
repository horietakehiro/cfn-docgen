import os

class AppConfig:
    APP_NAME="cfn-docgen"
    APP_ROOT_DIR=os.path.join(
        "~", f".{APP_NAME}"
    )

