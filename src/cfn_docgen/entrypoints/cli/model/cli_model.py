from dataclasses import dataclass
import os
from typing import Callable, Literal, List
from cfn_docgen.config import AppContext

from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.model.cfn_template import CfnTemplateSource
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenServiceCommandInput, SupportedFormat, ext_by_format


Subcommand = Literal["docgen"]


@dataclass
class CliArguement:
    subcommand:Subcommand
    format: SupportedFormat
    source: str
    dest: str
    debug: bool = False

    def as_list(self) -> List[str]:
        arg_list = [
            self.subcommand,
            "--format", self.format,
            "--source", self.source,
            "--dest", self.dest,
        ]
        if self.debug:
            arg_list.append("--debug")
        return arg_list
    
class CfnDocgenCLIUnitsOfWork:
    args:CliArguement
    units_of_work:List[CfnDocgenServiceCommandInput]

    def __init__(
        self,
        args:CliArguement,
        file_loader_factory:Callable[[CfnTemplateSource, AppContext], IFileLoader],
        context:AppContext,
    ) -> None:
        self.units_of_work = self.build_units_of_work(
            args=args,
            file_loader_factory=file_loader_factory,
            context=context,
        )
        try:
            assert len(self.units_of_work) > 0, "no valid template sources and document dests are provided"
        except AssertionError as ex:
            context.log_error(ex.args[0])
            raise ex

    def build_units_of_work(
        self, 
        args:CliArguement, 
        file_loader_factory:Callable[[CfnTemplateSource, AppContext], IFileLoader],
        context:AppContext,
    ) -> List[CfnDocgenServiceCommandInput]:
        try:
            loader = file_loader_factory(CfnTemplateSource(args.source, context=context), context)
            sources = loader.list(source=args.source)
            assert len(sources) > 0, f"failed to list template sources at [{args.source}]"
            context.log_debug(f"listed source template files [{'.'.join(sources)}]")
        except Exception as ex:
            context.log_error(str(ex))
            return []
        

        # determine dest type
        dests:List[str] = []
        try:
            # dest is a single file
            _, dest_ext = os.path.splitext(args.dest)
            if dest_ext[1:] in list(ext_by_format.values()):
                assert len(sources) == 1
                return [
                    CfnDocgenServiceCommandInput(
                        template_source=CfnTemplateSource(s, context=context),
                        document_dest=CfnDocumentDestination(args.dest, context=context),
                        fmt=args.format,
                    ) for s in sources
                ]
        except Exception:
            context.log_error(f"invalid arguement pattern: source {args.source} is a directory, while dest {args.dest} is a single file")
            return []

        try:
            # dest is a directory
            for s in sources:
                base_prefix, _ = os.path.splitext(os.path.basename(s))
                subdirs = s.replace(args.source, "")
                if subdirs.startswith("/"):
                    subdirs = subdirs[1:]
                dests.append(
                    os.path.join(
                        args.dest, os.path.dirname(subdirs), f"{base_prefix}.{ext_by_format[args.format]}"
                    )
                )
            assert len(sources) == len(dests)
            units_of_work = [
                CfnDocgenServiceCommandInput(
                    template_source=CfnTemplateSource(s, context=context),
                    document_dest=CfnDocumentDestination(t, context=context),
                    fmt=args.format,
                ) for s, t in zip(sources, dests)
            ]
            units_of_work = sorted(
                units_of_work,
                key=lambda u: (u.template_source.source, u.document_dest.dest)
            )
            return units_of_work
        except Exception:
            context.log_error(f"the number of template sources[{len(sources)}] and document dests[{len(dests)}] are missmatched")
            return []


    def provide(self) -> List[CfnDocgenServiceCommandInput]:
        return self.units_of_work
