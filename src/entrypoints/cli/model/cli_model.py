from dataclasses import dataclass
import os
from typing import Callable, Literal, List, Mapping

from domain.model.cfn_document_generator import CfnDocumentDestination
from domain.model.cfn_template import CfnTemplateSource
from domain.ports.internal.file_loader import IFileLoader

from domain.services.cfn_docgen_service import CfnDocgenServiceCommandInput, SupportedFormat

Subcommand = Literal["docgen"]
ext_by_format:Mapping[SupportedFormat, str] = {
    "markdown": "md",
}

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
        file_loader_factory:Callable[[CfnTemplateSource], IFileLoader],
    ) -> None:
        self.units_of_work = self.build_units_of_work(
            args=args,
            file_loader_factory=file_loader_factory,
        )

    def build_units_of_work(
        self, 
        args:CliArguement, 
        file_loader_factory:Callable[[CfnTemplateSource], IFileLoader]
    ) -> List[CfnDocgenServiceCommandInput]:
        loader = file_loader_factory(CfnTemplateSource(args.source))

        sources = loader.list(source=args.source)

        # determine dest type
        dests:List[str] = []
        # dest is a single file
        _, dest_ext = os.path.splitext(args.dest)
        if dest_ext[1:] in list(ext_by_format.values()):
            assert len(sources) == 1
            return [
                CfnDocgenServiceCommandInput(
                    template_source=CfnTemplateSource(s),
                    document_dest=CfnDocumentDestination(args.dest),
                    fmt=args.format,
                ) for s in sources
            ]
        
        # dest is a directory
        for s in sources:
            base_prefix, _ = os.path.splitext(os.path.basename(s))
            subdirs = s.replace(args.source, "")
            if subdirs.startswith("/"):
                subdirs = subdirs[1:]
            dests.append(
                os.path.join(args.dest, os.path.dirname(subdirs), f"{base_prefix}.{ext_by_format[args.format]}")
            )
        assert len(sources) == len(dests)
        return [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(s),
                document_dest=CfnDocumentDestination(t),
                fmt=args.format,
            ) for s, t in zip(sources, dests)
        ]


    def provide(self) -> List[CfnDocgenServiceCommandInput]:
        return self.units_of_work
