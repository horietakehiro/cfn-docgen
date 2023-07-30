from typing import Literal
from pydantic import BaseModel

SupportedFormat = Literal["markdown", ]

class CfnDocgenServiceConfig(BaseModel):

    fmt: SupportedFormat
    input_file: str
    output_file: str

