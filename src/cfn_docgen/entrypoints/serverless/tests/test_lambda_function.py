import logging
import pytest
import os
import boto3

from cfn_docgen.entrypoints.serverless import lambda_function
from cfn_docgen.entrypoints.serverless.model.lambda_model import S3NotificationEvent, S3NotificationEventRecord, S3NotificationEventRecordS3, S3NotificationEventRecordS3Bucket, S3NotificationEventRecordS3Object

INPUT_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "docs", "sample-template.yaml"
)
EXPECTED_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "docs", "sample-template.md"
)

# s3 bucket and objects
s3_client = boto3.client("s3") # type: ignore
TEST_BUCKET_NAME=os.environ["TEST_BUCKET_NAME"]
INPUT_ROOT_PREFIX=f"s3://{TEST_BUCKET_NAME}/data/input"
INPUT_PREFIX1=INPUT_ROOT_PREFIX+"/dir1"
INPUT_KEY1=INPUT_PREFIX1+"/sample-template.yaml"
INPUT_PREFIX2=INPUT_PREFIX1+"/dir2"
INPUT_KEY2=INPUT_PREFIX2+"/sample-template.yaml"

OUTPUT_ROOT_PREFIX=f"s3://{TEST_BUCKET_NAME}/data/output"
OUTPUT_PREFIX1=OUTPUT_ROOT_PREFIX+"/dir1"
OUTPUT_MD_KEY1=OUTPUT_PREFIX1+"/sample-template.md"
OUTPUT_PREFIX2=OUTPUT_PREFIX1+"/dir2"
OUTPUT_MD_KEY2=OUTPUT_PREFIX2+"/sample-template.md"


@pytest.fixture(scope="class", autouse=True)
def class_s3_bucket_and_keys():
    # cleanup s3 keys
    for prefix in [INPUT_ROOT_PREFIX, OUTPUT_ROOT_PREFIX]:
        res = s3_client.list_objects(
            Bucket=TEST_BUCKET_NAME,
            Prefix=prefix,
        )
        contents = res.get("Contents", None)
        if contents is None or len(contents) == 0: # type: ignore
            continue
        s3_client.delete_objects(
            Bucket=TEST_BUCKET_NAME,
            Delete={
                "Objects": [
                    {"Key": content["Key"]} for content in contents # type: ignore
                ]
            }
        )
    
    # prepare input keys
    for key in [INPUT_KEY1, INPUT_KEY2]:
        s3_client.upload_file(
            Bucket=TEST_BUCKET_NAME,
            Key=key,
            Filename=INPUT_MASTER_FILE
        )


@pytest.fixture(scope="function", autouse=True)
def function_s3_bucket_and_keys():
    # cleanup s3 keys
    res = s3_client.list_objects_v2(
        Bucket=TEST_BUCKET_NAME,
        Prefix=OUTPUT_ROOT_PREFIX,
    )
    contents = res.get("Contents", None)
    if contents is not None and len(contents) > 0: # type: ignore
        s3_client.delete_objects(
            Bucket=TEST_BUCKET_NAME,
            Delete={
                "Objects": [
                    {"Key": content["Key"]} for content in contents # type: ignore
                ]
            }
        )


def test_serverless():
    event = S3NotificationEvent(
        Records=[
            S3NotificationEventRecord(
                s3=S3NotificationEventRecordS3(
                    bucket=S3NotificationEventRecordS3Bucket(
                        name=TEST_BUCKET_NAME
                    ),
                    object=S3NotificationEventRecordS3Object(
                        key=INPUT_KEY1.replace(f"s3://{TEST_BUCKET_NAME}/", "")
                    )
                )
            ),
            S3NotificationEventRecord(
                s3=S3NotificationEventRecordS3(
                    bucket=S3NotificationEventRecordS3Bucket(
                        name=TEST_BUCKET_NAME
                    ),
                    object=S3NotificationEventRecordS3Object(
                        key=INPUT_KEY2.replace(f"s3://{TEST_BUCKET_NAME}/", "")
                    )
                )
            )
        ]
    )
    result = lambda_function.lambda_handler(event=event.model_dump(), context=None)
    assert len(result) == 2

    with open(EXPECTED_MASTER_FILE, "rb") as fp:
        expected = fp.read()
    res = s3_client.get_object(
        Bucket=lambda_function.DEST_BUCKET_NAME, 
        Key=os.path.join(
            lambda_function.DEST_BUCKET_PREFIX, os.path.dirname(INPUT_KEY1.replace(f"s3://{TEST_BUCKET_NAME}/", "")), "sample-template.md"
        ),
    )
    assert res["Body"].read() == expected
    res = s3_client.get_object(
        Bucket=lambda_function.DEST_BUCKET_NAME, 
        Key=os.path.join(
            lambda_function.DEST_BUCKET_PREFIX, os.path.dirname(INPUT_KEY2.replace(f"s3://{TEST_BUCKET_NAME}/", "")), "sample-template.md"
        ),
    )
    assert res["Body"].read() == expected



def test_serverless_continue(caplog:pytest.LogCaptureFixture):
    caplog.set_level(logging.WARNING)
    try:
        event = S3NotificationEvent(
            Records=[
                S3NotificationEventRecord(
                    s3=S3NotificationEventRecordS3(
                        bucket=S3NotificationEventRecordS3Bucket(
                            name=TEST_BUCKET_NAME
                        ),
                        object=S3NotificationEventRecordS3Object(
                            key=INPUT_KEY1.replace(f"s3://{TEST_BUCKET_NAME}/", "")
                        )
                    )
                ),
                S3NotificationEventRecord(
                    s3=S3NotificationEventRecordS3(
                        bucket=S3NotificationEventRecordS3Bucket(
                            name=TEST_BUCKET_NAME
                        ),
                        object=S3NotificationEventRecordS3Object(
                            key=INPUT_KEY2.replace(f"s3://{TEST_BUCKET_NAME}/", "")
                        )
                    )
                )
            ]
        )
        # replace partial file with invalid body
        s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=INPUT_KEY1.replace(f"s3://{TEST_BUCKET_NAME}/", ""), Body=b"invalid")

        result = lambda_function.lambda_handler(event=event.model_dump(), context=None)
        assert len(result) == 1

        warn_messages = [r.message for r in caplog.records if r.levelno == logging.WARNING]

        assert "failed to generate document" in warn_messages[0]

    finally:
        with open(INPUT_MASTER_FILE, "rb") as fp:
            s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=INPUT_KEY1.replace(f"s3://{TEST_BUCKET_NAME}/", ""), Body=fp.read())

