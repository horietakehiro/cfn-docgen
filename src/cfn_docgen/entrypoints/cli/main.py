import logging
import sys
from typing import Optional
import click
from cfn_docgen.adapters.cfn_document_storage import document_storage_facotory
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.cfn_template_provider import template_provider_factory
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import RemoteFileLoader, file_loader_factory
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import document_generator_factory
from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenService

from cfn_docgen.entrypoints.cli.model.cli_model import CfnDocgenCLIUnitsOfWork, CliArguement, SupportedFormat

@click.group(name="cfn-docgen")
@click.version_option(package_name="cfn-docgen")
def main():
    pass

@main.command()
@click.option(
    "-f", "--format", "fmt", required=False, type=click.Choice(["markdown"]), show_default=True, default="markdown",
    help="format of output file"
)
@click.option(
    "-s", "--source", "source", required=True, type=str, 
    help="input cfn template source. (can be file or directory with form of local path or S3 url)"
)
@click.option(
    "-d", "--dest", "dest", required=True, type=str, 
    help="output document destination. (can be file or directory with form of local path or S3 url)"
)
@click.option(
    "-p", "--profile", "profile", required=False, type=str, default=None,
    help="aws profile name."
)
@click.option(
    "--debug", "debug", required=False, is_flag=True, show_default=True, default=False,
    help="enable logging"
)
def docgen(fmt:SupportedFormat, source:str, dest:str, profile:Optional[str]=None, debug:bool=False):
    context = AppContext(
        request_id=None,
        logger_name="cfn-docgen",
        log_level=logging.DEBUG if debug else logging.CRITICAL,
        connection_settings=ConnectionSettings(
            aws=AwsConnectionSettings(profile_name=profile)
        )
    )
    args = CliArguement(
        subcommand="docgen",
        format=fmt,
        source=source,
        dest=dest,
    )
    context.log_debug(f"received args [{' '.join(args.as_list())}]")

    try:
        units_of_work = CfnDocgenCLIUnitsOfWork(
            args=args,
            file_loader_factory=file_loader_factory,
            context=context,
        )
    except AssertionError:
        context.log_error("failed to setup pairs of template sources and document dests")
        click.echo(context.log_messages.as_string(logging.INFO))
        sys.exit(1)

    try:
        service = CfnDocgenService(
            cfn_template_provider_facotry=template_provider_factory,
            cfn_document_generator_factory=document_generator_factory,
            cfn_document_storage_factory=document_storage_facotory,
            cfn_specification_repository=CfnSpecificationRepository(
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                loader=RemoteFileLoader(context=context),
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
                context=context,
            ),
            context=context,
        )
        
    except Exception:
        context.log_error("failed to setup CfnDocgenService")
        click.echo(context.log_messages.as_string(logging.INFO))
        sys.exit(1)

    for command_input in units_of_work.provide():
        try:
            context.log_debug(f"start cfn-docgen process for template source [{command_input.template_source.source}] and document dest [{command_input.document_dest.dest}]")
            result = service.main(command_input=command_input)
            context.log_info(f"successfully generate document [{result.document_dest}] from template [{command_input.template_source.source}]")
        except Exception:
            context.log_warning(f"failed to generate document [{command_input.document_dest.dest}] from template [{command_input.template_source.source}]")
            continue


    click.echo(context.log_messages.as_string(logging.INFO))
    sys.exit(0)
