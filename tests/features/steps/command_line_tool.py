# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring
from behave import given, then, when  # pylint: disable=no-name-in-module
import subprocess
import os

from environment import CommandLineToolContext
from setup import VERSION


@given("that cfn-docgen command line tool is locally installed")
def step_impl(context:CommandLineToolContext):
    installed_version = subprocess.check_output(["cfn-docgen", "--version"], ).decode()
    assert f"version {VERSION}" in installed_version, f"Source code version is {VERSION} but installed version is {installed_version}"

@given("CloudFormation template yaml file is locally saved")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.input_file), f"{context.input_file} does not exist"

@when("cfn-docgen is invoked, with specifying input file, output file, and output file format as markdown")
def step_impl(context:CommandLineToolContext):
    _ = subprocess.check_output([
        "cfn-docgen", "--format", context.format, 
        "--input-file", context.input_file,
        "--output-file", context.output_file,
    ])

@then("a single markdown document file is locally created")
def step_impl(context:CommandLineToolContext):
    assert os.path.exists(context.output_file), f"{context.output_file} does not exist"


@then("all of the definitions of CloudFormation template are written as a form of markdown in it.")
def step_imlp(context:CommandLineToolContext):
    raise NotImplementedError