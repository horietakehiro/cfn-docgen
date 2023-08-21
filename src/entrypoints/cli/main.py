import click
from adapters.cfn_document_storage import document_storage_facotory
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.cfn_template_provider import template_provider_factory
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader, file_loader_factory
from config import AppConfig
from domain.model.cfn_document_generator import document_generator_factory
from domain.services.cfn_docgen_service import CfnDocgenService

from src.entrypoints.cli.model.cli_model import CfnDocgenCLIUnitsOfWork, CliArguement, SupportedFormat


@click.group(name="cfn-docgen")
@click.version_option()
def main():
    pass

@main.command()
@click.option("--format", "fmt", required=True, type=click.Choice(["markdown"]), help="format of output file")
@click.option("--source", "source", required=True, type=str, help="input cfn template source. (can be file or directory with form of local path or S3 url)")
@click.option("--dest", "dest", required=True, type=str, help="output document destination. (can be file or directory with form of local path or S3 url)")
def docgen(fmt:SupportedFormat, source:str, dest:str):

    units_of_work = CfnDocgenCLIUnitsOfWork(
        args=CliArguement(
            subcommand="docgen",
            format=fmt,
            source=source,
            dest=dest,
        ),
        file_loader_factory=file_loader_factory,
    )

    service = CfnDocgenService(
        cfn_template_provider_facotry=template_provider_factory,
        cfn_document_generator_factory=document_generator_factory,
        cfn_document_storage_factory=document_storage_facotory,
        cfn_specification_repository=CfnSpecificationRepository(
            source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
            loader=RemoteFileLoader(),
            cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
            recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        )
    )

    for command_input in units_of_work.provide():
        result = service.main(command_input=command_input)
        click.echo(result.document_dest)



