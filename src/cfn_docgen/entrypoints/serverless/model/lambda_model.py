import os
from typing import List

from pydantic import BaseModel
from dataclasses import dataclass
from cfn_docgen.config import AppContext

from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.model.cfn_template import CfnTemplateSource
from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenServiceCommandInput, SupportedFormat, ext_by_format

class S3NotificationEventRecordS3Object(BaseModel):
    key: str
class S3NotificationEventRecordS3Bucket(BaseModel):
    name: str
class S3NotificationEventRecordS3(BaseModel):
    bucket: S3NotificationEventRecordS3Bucket
    object: S3NotificationEventRecordS3Object
class S3NotificationEventRecord(BaseModel):
    s3: S3NotificationEventRecordS3
class S3NotificationEvent(BaseModel):
    Records: List[S3NotificationEventRecord]



@dataclass
class ServerlessArguement:
    format: SupportedFormat
    sources:List[S3NotificationEventRecordS3]
    dest_bucket:str
    dest_prefix:str
    
class CfnDocgenServerlessUnitsOfWork:
    def __init__(
        self,
        args:ServerlessArguement,
        context:AppContext,
    ) -> None:
        self.units_of_work = self.build_units_of_work(
            args=args,
            context=context,
        )
        try:
            assert len(self.units_of_work) > 0, "no valid template sources and document dests are proided"
        except AssertionError as ex:
            context.log_error(ex.args[0])
            raise ex

    def build_units_of_work(
        self, 
        args:ServerlessArguement, 
        context:AppContext,
    ) -> List[CfnDocgenServiceCommandInput]:
        
        units_of_work:List[CfnDocgenServiceCommandInput] = []

        try:
            # source must be a single file
            for source in args.sources:
                bucket = source.bucket.name
                key = source.object.key

                source_dir = os.path.dirname(key)
                base_prefix, _ = os.path.splitext(os.path.basename(key))
                dest_bucket = args.dest_bucket
                dest_prefix = args.dest_prefix
                if dest_prefix.endswith("/"):
                    dest_prefix = dest_prefix[:-1]

                units_of_work.append(
                    CfnDocgenServiceCommandInput(
                        template_source=CfnTemplateSource(f"s3://{bucket}/{key}", context=context),
                        document_dest=CfnDocumentDestination(
                            f"s3://{dest_bucket}/{dest_prefix}/{source_dir}/{base_prefix}.{ext_by_format[args.format]}",
                            context=context,
                        ),
                        fmt=args.format,
                    )
                )
            return units_of_work
        except Exception:
            context.log_error("failed to prepare template sources and document dests")
            return []

    def provide(self) -> List[CfnDocgenServiceCommandInput]:
        return self.units_of_work
