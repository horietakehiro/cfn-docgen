import logging
import sys
from typing import Optional
import click
from cfn_docgen.adapters.cfn_document_storage import document_storage_facotory
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.cfn_template_provider import template_provider_factory
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory, template_loader_factory
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import document_generator_factory
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationResourceTypeName
from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenService
from cfn_docgen.domain.services.cfn_skelton_service import CfnSkeltonService, CfnSkeltonServiceCommandInput, SkeltonFormat

from cfn_docgen.entrypoints.cli.model.cli_model import CfnDocgenCLIUnitsOfWork, CliDocgenArguement, SupportedFormat

@click.group(name="cfn-docgen")
@click.version_option(package_name="cfn-docgen")
def main():
    pass

@main.command()
@click.option(
    "-t", "--type", "skelton_type", required=False, type=str, default=None,
    help="skelton type to be shown (e.g. AWS::EC2::Instance, or Custom::any)"
)
@click.option(
    "-l", "--list", "list_", required=False, is_flag=True, show_default=True, default=False,
    help="show list of supproted resource types",
)
@click.option(
    "-c", "--custom-resource-specification", "custom_resource_specification", required=False, type=str, default=None,
    help="local file path or S3 URL for your custom resource specification json file"
)
@click.option(
    "-f", "--format", "fmt", type=click.Choice(["yaml", "json"]), show_default=True, default="yaml",
    help="format of skelton"
)
@click.option(
    "--debug", "debug", required=False, is_flag=True, show_default=True, default=False,
    help="enable logging"
)
def skelton(
    skelton_type:Optional[str]=None, 
    custom_resource_specification:Optional[str]=None, 
    list_:bool=False, debug:bool=False,
    fmt: SkeltonFormat="yaml",
):
    context = AppContext(
        log_level=logging.DEBUG if debug else logging.INFO
    )
    try:
        if skelton_type is not None:
            command_input = CfnSkeltonServiceCommandInput(
                type=CfnSpecificationResourceTypeName(skelton_type, context),
                list=list_,
                format=fmt,
            )
        else:
            command_input = CfnSkeltonServiceCommandInput(
                type=None,
                list=list_,
                format=fmt,
            )
        
        service = CfnSkeltonService(
            cfn_specification_repository=CfnSpecificationRepository(
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                custom_resource_specification_url=custom_resource_specification,
                loader_factory=specification_loader_factory,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
                context=context,
            ),
            context=context,
        )
        command_output = service.main(command_input)
        click.echo(command_output.skelton)

        if not list_:
            context.log_info(
                f"for more information about [{command_output.type}], see [{command_output.document_url}]"
            )
        sys.exit(0)

    except Exception:
        context.log_error(f"skelton for [{skelton_type}] failed to be shown")
        click.echo(context.log_messages.as_string(level=logging.ERROR))
        sys.exit(1)



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
    "-c", "--custom-resource-specification", "custom_resource_specification", required=False, type=str, default=None,
    help="local file path or S3 URL for your custom resource specification json file"
)
@click.option(
    "--debug", "debug", required=False, is_flag=True, show_default=True, default=False,
    help="enable logging"
)
def docgen(
    fmt:SupportedFormat, 
    source:str,
    dest:str, 
    custom_resource_specification:str,
    profile:Optional[str]=None, 
    debug:bool=False,
):
    context = AppContext(
        request_id=None,
        logger_name="cfn-docgen",
        log_level=logging.DEBUG if debug else logging.CRITICAL,
        connection_settings=ConnectionSettings(
            aws=AwsConnectionSettings(profile_name=profile)
        )
    )
    args = CliDocgenArguement(
        subcommand="docgen",
        format=fmt,
        source=source,
        dest=dest,
    )
    context.log_debug(f"received args [{' '.join(args.as_list())}]")

    try:
        units_of_work = CfnDocgenCLIUnitsOfWork(
            args=args,
            file_loader_factory=template_loader_factory,
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
                custom_resource_specification_url=custom_resource_specification,
                loader_factory=specification_loader_factory,
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
