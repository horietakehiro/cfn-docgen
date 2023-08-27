

import os
from typing import Any, List, Mapping, Optional
from cfn_docgen.adapters.cfn_document_storage import document_storage_facotory
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.cfn_template_provider import template_provider_factory
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import RemoteFileLoader
from cfn_docgen.config import AppConfig
from cfn_docgen.domain.model.cfn_document_generator import document_generator_factory
from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenService, CfnDocgenServiceCommandOutput
# from cfn_docgen.entrypoints.cli.model.cli_model import CfnDocgenCLIUnitsOfWork, CliArguement
from cfn_docgen.entrypoints.serverless.model.lambda_model import CfnDocgenServerlessUnitsOfWork, S3NotificationEvent, ServerlessArguement

DEST_BUCKET_NAME=os.environ["DEST_BUCKET_NAME"]
DEST_BUCKET_PREFIX=os.environ["DEST_BUCKET_PREFIX"]
if DEST_BUCKET_PREFIX.startswith("/"):
    DEST_BUCKET_PREFIX = DEST_BUCKET_PREFIX[1:] # type: ignore

def lambda_handler(event:Mapping[str, Optional[Any]], context:Any) -> List[str]:
    s3_notification_event = S3NotificationEvent(**event) # type: ignore
    outputs:List[CfnDocgenServiceCommandOutput] = []

    units_of_work = CfnDocgenServerlessUnitsOfWork(
        args=ServerlessArguement(
            format="markdown",
            sources=[r.s3 for r in s3_notification_event.Records],
            dest_bucket=DEST_BUCKET_NAME,
            dest_prefix=DEST_BUCKET_PREFIX,
        ),
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
        outputs.append(result)

    return [o.document_dest for o in outputs]