import logging
import pytest
from cfn_docgen.config import AppContext
from cfn_docgen.entrypoints.serverless.model.lambda_model import CfnDocgenServerlessUnitsOfWork, S3NotificationEventRecordS3, S3NotificationEventRecordS3Bucket, S3NotificationEventRecordS3Object, ServerlessArguement

@pytest.fixture
def context():
    return AppContext(log_level=logging.DEBUG)

def test_CfnDocgenServerlessUnitsOfWork_build_units_of_work(context:AppContext):
    args = ServerlessArguement(
        format="markdown",
        sources=[
            S3NotificationEventRecordS3(
                bucket=S3NotificationEventRecordS3Bucket(name="test-bucket"),
                object=S3NotificationEventRecordS3Object(
                    key="templates/dir1/sample-template.yaml",
                )
            ),
            S3NotificationEventRecordS3(
                bucket=S3NotificationEventRecordS3Bucket(name="test-bucket"),
                object=S3NotificationEventRecordS3Object(
                    key="templates/dir2/sample-template.yaml",
                )
            )
        ],
        dest_bucket="dest-bucket",
        dest_prefix="documents/"
    )

    units_of_work = CfnDocgenServerlessUnitsOfWork(args, context=context).provide()

    assert len(units_of_work) == 2
    assert units_of_work[0].template_source.source == "s3://test-bucket/templates/dir1/sample-template.yaml"
    assert units_of_work[1].template_source.source == "s3://test-bucket/templates/dir2/sample-template.yaml"
    assert units_of_work[0].document_dest.dest == "s3://dest-bucket/documents/templates/dir1/sample-template.md"
    assert units_of_work[1].document_dest.dest == "s3://dest-bucket/documents/templates/dir2/sample-template.md"

def test_CfnDocgenServerlessUnitsOfWork_build_units_of_work_fail(context:AppContext):
    with pytest.raises(AssertionError):
        args = ServerlessArguement(
            format="markdown",
            sources=[
                S3NotificationEventRecordS3(
                    bucket=S3NotificationEventRecordS3Bucket(name="test-bucket"),
                    object=S3NotificationEventRecordS3Object(
                        key="templates/dir1/sample-template.yaml",
                    )
                ),
                S3NotificationEventRecordS3(
                    bucket=S3NotificationEventRecordS3Bucket(name="test-bucket"),
                    object=S3NotificationEventRecordS3Object(
                        key="templates/dir2/sample-template.yaml",
                    )
                )
            ],
            dest_bucket="dest-bucket",
            dest_prefix=None, # type: ignore
        )
        CfnDocgenServerlessUnitsOfWork(args, context=context)

    assert "no valid template sources and document dests are proided" in context.log_messages.as_string(level=logging.ERROR)
