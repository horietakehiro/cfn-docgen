# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring
import os
import subprocess

from behave import given, then, when  # pylint: disable=no-name-in-module

from setup import VERSION
from tests.features.environment import CommandLineToolContext

@given("cfn-docgen command line tool is locally installed")
def step_impl(context:CommandLineToolContext):
    installed_version = subprocess.check_output(["cfn-docgen", "--version"], ).decode()
    assert f"version {VERSION}" in installed_version, f"Source code version is {VERSION} but installed version is {installed_version}"

@given("CloudFormation template file is locally saved")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.source), f"{context.source} does not exist"

@when("cfn-docgen is invoked, with specifying source and dest, and format as markdown")
def step_impl(context:CommandLineToolContext):
    _ = subprocess.check_output([
        "cfn-docgen", "docgen",
        "--format", context.format, 
        "--source", context.source,
        "--dest", context.dest,
    ])

@then("a single markdown document file is locally created")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.dest), f"{context.dest} does not exist"

@then("all of the definitions of CloudFormation template are written as a form of markdown in it.")
def step_imlp(context:CommandLineToolContext):
    with open(context.expected, "r", encoding="UTF8") as fp:
        expected = fp.read()
    with open(context.dest, "r", encoding="UTF-8") as fp:
        output = fp.read()

    assert output == expected
