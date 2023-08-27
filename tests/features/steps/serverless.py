# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring
import time
from urllib.parse import urlparse

from behave import given, then, when
import boto3  # pylint: disable=no-name-in-module

from tests.features.environment import INPUT_MASTER_FILE, ServerlessContext

@given("cfn-docgen serverless application is deployed")
def step_impl(context:ServerlessContext):
    cfn_client = boto3.client("cloudformation") # type: ignore
    res = cfn_client.describe_stacks(
        StackName=context.stack_name,
    )
    assert res["Stacks"][0]["StackName"] == context.stack_name


@when("CloudFormation template file is uploaded to S3 bucket")
def step_impl(context:ServerlessContext):
    s3 = boto3.client("s3") # type: ignore
    source_url = urlparse(context.source)
    bucket = source_url.netloc
    key = source_url.path
    if key.startswith("/"):
        key = key[1:]

    with open(INPUT_MASTER_FILE, "rb") as fp:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=fp.read()
        )

@then("markdown document files are created and uploaded to S3 bucket")
def step_impl(context:ServerlessContext):
    retry_count = 5
    current = 0
    s3 = boto3.client("s3") # type: ignore
    while current <= retry_count:
        try:
            for e in context.expected:
                s3_url = urlparse(e)
                bucket = s3_url.netloc
                key = s3_url.path
                if key.startswith("/"):
                    key = key[1:]
                res = s3.get_object(
                    Bucket=bucket,
                    Key=key,
                )
                with open(context.master, "rb") as fp:
                    assert res["Body"].read() == fp.read()
                continue
            break
        except Exception as ex:
            if "NoSuchKey" in str(ex):
                current += 1
                time.sleep(1)
                continue
            else:
                raise ex
    if current > retry_count:
        raise AssertionError