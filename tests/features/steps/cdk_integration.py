# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring
import os
import subprocess

from behave import given, then, when

from cfn_docgen import __version__
from tests.features.environment import CommandLineToolContext

@given("AWS-CDK-generated template json file is saved locally")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.source), f"{context.source} does not exist"

@when("Invoke cfn-docgen to generate document from AWS-CDK-generated template json file")
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


@then("markdown document file is locally created and embeded metadatas are written in it")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.dest)

    with open(context.dest, "r", encoding="UTF-8") as fp:
        doc = fp.read()
    assert "top-level-description" in doc
    assert "resource-level-description" in doc
