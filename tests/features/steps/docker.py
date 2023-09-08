# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring

import os
from urllib.parse import urlparse
import boto3
from behave import given, then, when

from tests.features.environment import DockerContext
from cfn_docgen import VERSION

@given("cfn-docgen docker image is installed locally")
def step_impl(context:DockerContext):
    context.docker_client.images.get(f"horietakehiro/cfn-docgen:{VERSION}") # type: ignore

@when("Invoke cfn-docgen as docker container")
def step_impl(context:DockerContext):
    context.docker_client.containers.run( # type: ignore
        f"horietakehiro/cfn-docgen:{VERSION}",
        command=f"docgen -f markdown -s {context.source} -d {context.dest} --debug",
        remove=True,
        volumes={
            os.path.join(os.path.expanduser("~"), ".aws") : {"bind": "/root/.aws", "mode": "ro"}
            # os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs") : {"bind": "/tmp/", "mode": "rw"},
            # "/tmp/cfn-docgen-test/" : {"bind": "/out/", "mode": "rw"},
        }
    )


@then("markdown document files are created and saved")
def step_impl(context:DockerContext):

    s3 = boto3.client("s3") # type: ignore
    for e in context.expected:
        s3_url = urlparse(e)
        bucket = s3_url.netloc
        prefix_or_key = s3_url.path
        if prefix_or_key.startswith("/"):
            prefix_or_key = prefix_or_key[1:]
        res = s3.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix_or_key
        )
        assert len(res["Contents"]) == 1