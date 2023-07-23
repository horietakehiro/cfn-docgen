""""""
from dataclasses import dataclass
from typing import Literal, List

SupportedFormat = Literal["markdown", ]
Subcommand = Literal["docgen"]

@dataclass
class CliArguement:
    subcommand:Subcommand
    format: SupportedFormat
    input_file: str
    output_file: str

    def as_list(self) -> List[str]:
        return [
            self.subcommand,
            "--format", self.format,
            "--input-file", self.input_file,
            "--output-file", self.output_file,
        ]