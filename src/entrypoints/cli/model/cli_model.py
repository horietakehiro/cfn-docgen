from dataclasses import dataclass
from typing import Callable, Literal, List
from adapters.cfn_template_provider import template_provider_factory
from domain.model.cfn_document_generator import CfnDocumentDestination
from domain.model.cfn_template import CfnTemplateSource
from domain.ports.cfn_template_provider import ICfnTemplateProvider

from domain.services.cfn_docgen_service import CfnDocgenServiceCommandInput, SupportedFormat

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
    
class CfnDocgenCLIUnitsOfWork:
    args:CliArguement
    units_of_work:List[CfnDocgenServiceCommandInput]

    def __init__(
        self,
        args:CliArguement,
        file_loader_factory:Callable[[CfnTemplateSource], ICfnTemplateProvider],
    ) -> None:
        self.units_of_work = self.build_units_of_work(args)

    def build_units_of_work(
        self, 
        args:CliArguement, 
        file_loader_factory:Callable[[CfnTemplateSource], ICfnTemplateProvider]
    ) -> List[CfnDocgenServiceCommandInput]:
        loader = file_loader_factory(CfnTemplateSource(args.source))

        loader 



    def provide(self) -> List[CfnDocgenServiceCommandInput]:
        pass
