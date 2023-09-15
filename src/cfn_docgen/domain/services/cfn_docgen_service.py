from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import Callable, Mapping
from cfn_docgen.adapters.cfn_document_storage import document_storage_facotory
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.cfn_template_provider import template_provider_factory
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
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
        cfn_template_provider_facotry:Callable[[CfnTemplateSource, AppContext], ICfnTemplateProvider],
        cfn_document_generator_factory:Callable[[SupportedFormat, AppContext], ICfnDocumentGenerator],
        cfn_document_storage_factory:Callable[[CfnDocumentDestination, AppContext], ICfnDocumentStorage],
        cfn_specification_repository:ICfnSpecificationRepository,
        context:AppContext,
    ) -> None:
        self.context = context
        try:
            self.template_provider_factory = cfn_template_provider_facotry
            self.document_generator_factory = cfn_document_generator_factory
            self.document_storage_factory = cfn_document_storage_factory
            self.spec_repository = cfn_specification_repository
        except Exception as ex:
            self.context.log_error("failed to setup cfn-docgen service")
            raise ex

    def main(self, command_input:CfnDocgenServiceCommandInput) -> CfnDocgenServiceCommandOutput:
        try:
            template_definition = self.template_provider_factory(
                command_input.template_source,
                self.context,
            ).load_template(
                command_input.template_source,
            )
        except Exception as ex:
            self.context.log_error(
                f"failed to load template from [{command_input.template_source.source}]"
            )
            raise ex

        try:
            template_tree = CfnTemplateTree(
                template_source=command_input.template_source,
                definition=template_definition,
                spec_repository=self.spec_repository,
                context=self.context,
            )
        except Exception as ex:
            self.context.log_error("failed to build CfnTemplateTree")
            raise ex

        try:
            document = self.document_generator_factory(
                command_input.fmt,
                self.context,
            ).generate(
                cfn_template_tree=template_tree,
            )
        except Exception as ex:
            self.context.log_error(f"failed to generate [{command_input.fmt}] document")
            raise ex
        try:
            self.document_storage_factory(
                command_input.document_dest,
                self.context,
            ).save_document(
                body=document.encode(encoding="UTF-8"),
                document_dest=command_input.document_dest,
            )
        except Exception as ex:
            self.context.log_error(f"failed to save [{command_input.fmt}] document")
            raise ex
        
        return CfnDocgenServiceCommandOutput(
            document_dest=command_input.document_dest.dest,
        )


    @classmethod
    def with_default(cls) -> CfnDocgenService:
        context = AppContext(
            log_level=logging.CRITICAL,
            connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
        )
        return CfnDocgenService(
            context=context,
            cfn_template_provider_facotry=template_provider_factory,
            cfn_document_generator_factory=document_generator_factory,
            cfn_document_storage_factory=document_storage_facotory,
            cfn_specification_repository=CfnSpecificationRepository(
                context=context,
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                loader_factory=specification_loader_factory,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            )
        )