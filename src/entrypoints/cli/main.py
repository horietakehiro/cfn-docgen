import click
from adapters.cfn_document_storage import document_storage_facotory
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.cfn_template_provider import template_provider_factory
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig
from domain.model.cfn_document_generator import CfnDocumentDestination, document_generator_factory
from domain.model.cfn_template import CfnTemplateSource
from domain.services.cfn_docgen_service import CfnDocgenService, CfnDocgenServiceCommandInput

from src.entrypoints.cli.model.cli_model import SupportedFormat

@click.group(name="cfn-docgen")
@click.version_option()
def main():
    pass

@main.command()
@click.option("--format", "fmt", required=True, type=click.Choice(["markdown"]), help="format of output file")
@click.option("--source", "source", required=True, type=str, help="input cfn template source")
@click.option("--dest", "dest", required=True, type=str, help="output document destination")
def docgen(fmt:SupportedFormat, source:str, dest:str):
    command_input = CfnDocgenServiceCommandInput(
        template_source=CfnTemplateSource(source=source),
        document_dest=CfnDocumentDestination(dest=dest),
        fmt=fmt,
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

    service.main(command_input=command_input)



