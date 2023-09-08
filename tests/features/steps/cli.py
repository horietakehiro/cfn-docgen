# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring
import os
import subprocess
from urllib.parse import urlparse

from behave import given, then, when
import boto3  # pylint: disable=no-name-in-module

from cfn_docgen import __version__
from tests.features.environment import CommandLineToolContext

@given("cfn-docgen command line tool is locally installed")
def step_impl(context:CommandLineToolContext):
    installed_version = subprocess.check_output(["cfn-docgen", "--version"], ).decode()
    assert f"version {__version__}" in installed_version, f"Source code version is {__version__} but installed version is {installed_version}"

@given("CloudFormation template files are locally saved")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.source), f"{context.source} does not exist"

@given("CloudFormation template files are saved at S3 bucket")
def step_impl(context:CommandLineToolContext):
    s3 = boto3.client("s3") # type: ignore
    source_url = urlparse(context.source)
    bucket = source_url.netloc
    prefix_or_key = source_url.path
    if prefix_or_key.startswith("/"):
        prefix_or_key = prefix_or_key[1:]

    res = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix_or_key
    )
    assert len(res["Contents"]) > 0

@when("cfn-docgen is invoked, with specifying source and dest, and format as markdown")
def step_impl(context:CommandLineToolContext):
    resutl = subprocess.run(
        [
            "cfn-docgen", "docgen",
            "--format", context.format, 
            "--source", context.source,
            "--dest", context.dest,
        ],
        check=True,
        capture_output=True,
    )
    assert resutl.returncode == 0, f"command failed with {resutl.returncode}, {resutl.stdout}, {resutl.stderr}"


@then("markdown document files are locally created")
def step_impl(context:CommandLineToolContext):
    for e in context.expected:
        assert os.path.exists(e), f"{e} does not exists"

@then("markdown document files are created at S3 bucket")
def step_impl(context:CommandLineToolContext):
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

@then("all of the definitions of CloudFormation template are written as a form of markdown in it.")
def step_imlp(context:CommandLineToolContext):
    with open(context.master, "r", encoding="UTF-8") as fp:
        master = fp.read()
    for e in context.expected:
        with open(e, "r", encoding="UTF8") as fp:
            expected = fp.read()

        assert expected == master
