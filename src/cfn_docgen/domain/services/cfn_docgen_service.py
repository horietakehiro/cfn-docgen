from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping
from cfn_docgen.adapters.cfn_document_storage import document_storage_facotory
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.cfn_template_provider import template_provider_factory
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import RemoteFileLoader
from cfn_docgen.config import AppConfig
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination, ICfnDocumentGenerator, SupportedFormat, document_generator_factory
from cfn_docgen.domain.model.cfn_template import CfnTemplateSource, CfnTemplateTree
from cfn_docgen.domain.ports.cfn_document_storage import ICfnDocumentStorage
from cfn_docgen.domain.ports.cfn_specification_repository import ICfnSpecificationRepository
from cfn_docgen.domain.ports.cfn_template_provider import ICfnTemplateProvider

@dataclass
class CfnDocgenServiceCommandInput:
    template_source:CfnTemplateSource
    document_dest:CfnDocumentDestination
    fmt: SupportedFormat
@dataclass
class CfnDocgenServiceCommandOutput:
    document_dest: str

ext_by_format:Mapping[SupportedFormat, str] = {
    "markdown": "md",
}


class CfnDocgenService(object):

    def __init__(
        self, 
        cfn_template_provider_facotry:Callable[[CfnTemplateSource], ICfnTemplateProvider],
        cfn_document_generator_factory:Callable[[SupportedFormat], ICfnDocumentGenerator],
        cfn_document_storage_factory:Callable[[CfnDocumentDestination], ICfnDocumentStorage],
        cfn_specification_repository:ICfnSpecificationRepository,
    ) -> None:
        self.template_provider_factory = cfn_template_provider_facotry
        self.document_generator_factory = cfn_document_generator_factory
        self.document_storage_factory = cfn_document_storage_factory
        self.spec_repository = cfn_specification_repository


    def main(self, command_input:CfnDocgenServiceCommandInput) -> CfnDocgenServiceCommandOutput:
        template_definition = self.template_provider_factory(
            command_input.template_source,
        ).load_template(
            command_input.template_source,
        )
        template_tree = CfnTemplateTree(
            template_source=command_input.template_source,
            definition=template_definition,
            spec_repository=self.spec_repository,
        )

        document = self.document_generator_factory(
            command_input.fmt,
        ).generate(
            cfn_template_tree=template_tree,
        )

        self.document_storage_factory(
            command_input.document_dest
        ).save_document(
            body=document.encode(encoding="UTF-8"),
            document_dest=command_input.document_dest,
        )
        return CfnDocgenServiceCommandOutput(
            document_dest=command_input.document_dest.dest,
        )


    @classmethod
    def with_default(cls) -> CfnDocgenService:
        return CfnDocgenService(
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