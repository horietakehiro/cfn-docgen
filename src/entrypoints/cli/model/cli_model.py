from dataclasses import dataclass
from typing import Literal, List

from domain.services.cfn_docgen_service import SupportedFormat

Subcommand = Literal["docgen"]

@dataclass
class CliArguement:
    subcommand:Subcommand
    format: SupportedFormat
    source: str
    dest: str

    def as_list(self) -> List[str]:
        return [
            self.subcommand,
            "--format", self.format,
            "--source", self.source,
            "--dest", self.dest,
        ]