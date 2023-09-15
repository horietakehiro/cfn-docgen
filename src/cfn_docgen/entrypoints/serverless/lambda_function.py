# pylint: disable=W0613
import logging
import os
from typing import Any, List, Mapping, Optional
from cfn_docgen.adapters.cfn_document_storage import document_storage_facotory
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.cfn_template_provider import template_provider_factory
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import document_generator_factory
from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenService, CfnDocgenServiceCommandOutput
from cfn_docgen.entrypoints.serverless.model.lambda_model import CfnDocgenServerlessUnitsOfWork, S3NotificationEvent, ServerlessArguement

DEST_BUCKET_NAME=os.environ["DEST_BUCKET_NAME"]
DEST_BUCKET_PREFIX=os.environ["DEST_BUCKET_PREFIX"]
if DEST_BUCKET_PREFIX.startswith("/"):
    DEST_BUCKET_PREFIX = DEST_BUCKET_PREFIX[1:] # type: ignore
CUSTOM_RESOURCE_SPECIFICATION_URL=os.environ.get("CUSTOM_RESOURCE_SPECIFICATION_URL", None)

def lambda_handler(event:Mapping[str, Optional[Any]], context:Any) -> List[str]:
    outputs:List[CfnDocgenServiceCommandOutput] = []
    app_context = AppContext(
        log_level=logging.INFO,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

    try:
        s3_notification_event = S3NotificationEvent(**event) # type: ignore
    except Exception:
        app_context.log_error("failed to parse event. received request event may not be a S3 Notification Event.")
        return []
        
    try:
        units_of_work = CfnDocgenServerlessUnitsOfWork(
            args=ServerlessArguement(
                format="markdown",
                sources=[r.s3 for r in s3_notification_event.Records],
                dest_bucket=DEST_BUCKET_NAME,
                dest_prefix=DEST_BUCKET_PREFIX,
            ),
            context=app_context,
        )
    except Exception:
        app_context.log_error("failed to setup pairs of template sources and document dests")
        return []
    
    try:
        service = CfnDocgenService(
            cfn_template_provider_facotry=template_provider_factory,
            cfn_document_generator_factory=document_generator_factory,
            cfn_document_storage_factory=document_storage_facotory,
            cfn_specification_repository=CfnSpecificationRepository(
                context=app_context,
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                custom_resource_specification_url=CUSTOM_RESOURCE_SPECIFICATION_URL,
                loader_factory=specification_loader_factory,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=app_context),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            ),
            context=app_context,
        )
    except Exception:
        app_context.log_error("failed to setup CfnDocgenService")
        return []

    for command_input in units_of_work.provide():
        try:
            app_context.log_debug(f"start cfn-docgen process for template source [{command_input.template_source.source}] and document dest [{command_input.document_dest.dest}]")
            result = service.main(command_input=command_input)
            app_context.log_info(f"successfully generate document [{result.document_dest}] from template [{command_input.template_source.source}]")
            outputs.append(result)
        except Exception:
            app_context.log_warning(f"failed to generate document [{command_input.document_dest.dest}] from template [{command_input.template_source.source}]")
            continue

    print(app_context.log_messages.as_string(logging.INFO))
    return [o.document_dest for o in outputs]