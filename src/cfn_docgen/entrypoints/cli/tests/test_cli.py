import json
import logging
from typing import Optional
import pytest
import os
import shutil
import boto3
from click.testing import CliRunner
from cfn_docgen.domain.model.cfn_template import CfnTemplateResourceDefinition

from cfn_docgen.entrypoints.cli.main import main
from cfn_docgen.entrypoints.cli.model.cli_model import CliDocgenArguement, CliSkeltonArguement

INPUT_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "docs", "sample-template.yaml"
)
EXPECTED_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "docs", "sample-template.md"
)

# local directories and files
INPUT_ROOT_DIR=os.path.join(os.path.dirname(__file__), "data", "input")
INPUT_DIR1 = os.path.join(INPUT_ROOT_DIR, "dir1")
INPUT_FILE1 = os.path.join(INPUT_DIR1, "sample-template.yaml")
INPUT_DIR2 = os.path.join(INPUT_DIR1, "dir2")
INPUT_FILE2 = os.path.join(INPUT_DIR2, "sample-template.yaml")

OUTPUT_ROOT_DIR=os.path.join(os.path.dirname(__file__), "data", "output")
OUTPUT_DIR1 = os.path.join(OUTPUT_ROOT_DIR, "dir1")
OUTPUT_MD_FILE1 = os.path.join(OUTPUT_DIR1, "sample-template.md")
OUTPUT_DIR2 = os.path.join(OUTPUT_DIR1, "dir2")
OUTPUT_MD_FILE2 = os.path.join(OUTPUT_DIR2, "sample-template.md")


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

CUSTOM_RESOURCE_SPECIFICATION=os.path.join(
    os.path.dirname(__file__),
    "..", "..","..", "..","..", "docs", "custom-specification.json"
)

@pytest.fixture(scope="class", autouse=True)
def class_local_dirs_and_files():
    # cleanup local dirs
    shutil.rmtree(INPUT_ROOT_DIR, ignore_errors=True)
    shutil.rmtree(OUTPUT_ROOT_DIR, ignore_errors=True)

    # prepare input files and dirs
    os.makedirs(INPUT_DIR2, exist_ok=True)
    shutil.copy(INPUT_MASTER_FILE, INPUT_FILE1)
    shutil.copy(INPUT_MASTER_FILE, INPUT_FILE2)


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
def function_local_dirs_and_files():
    # cleanup output dirs
    shutil.rmtree(OUTPUT_ROOT_DIR, ignore_errors=True)

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


def test_cli_local_file_source_local_file_dest():
    args = CliDocgenArguement(
        subcommand="docgen",
        format="markdown",
        source=INPUT_FILE1,
        dest=OUTPUT_MD_FILE1,
    )

    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    with open(OUTPUT_MD_FILE1, "rb") as fp:
        output = fp.read()
    with open(EXPECTED_MASTER_FILE, "rb") as fp:
        example = fp.read()
    
    assert output == example


def test_cli_s3_key_source_s3_key_dest():
    args = CliDocgenArguement(
        subcommand="docgen",
        format="markdown",
        source=f"s3://{TEST_BUCKET_NAME}/{INPUT_KEY1}",
        dest=f"s3://{TEST_BUCKET_NAME}/{OUTPUT_MD_KEY1}",
    )
    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    with open(EXPECTED_MASTER_FILE, "rb") as fp:
        expected = fp.read()
    res = s3_client.get_object(
        Bucket=TEST_BUCKET_NAME, Key=OUTPUT_MD_KEY1,
    )
    assert res["Body"].read() == expected


def test_cli_local_folder_source_local_folder_dest():
    args = CliDocgenArguement(
        subcommand="docgen",
        format="markdown",
        source=INPUT_ROOT_DIR,
        dest=OUTPUT_ROOT_DIR,
    )

    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    with open(EXPECTED_MASTER_FILE, "r") as fp:
        expected = fp.read()
    
    for output_file in [OUTPUT_MD_FILE1, OUTPUT_MD_FILE2]:
        with open(output_file, "r") as fp:
            assert fp.read() == expected

def test_cli_s3_prefix_source_s3_prefix_dest():
    args = CliDocgenArguement(
        subcommand="docgen",
        format="markdown",
        source=f"s3://{TEST_BUCKET_NAME}/{INPUT_ROOT_PREFIX}",
        dest=f"s3://{TEST_BUCKET_NAME}/{OUTPUT_ROOT_PREFIX}",
    )
    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    with open(EXPECTED_MASTER_FILE, "rb") as fp:
        expected = fp.read()
    
    for output_key in [OUTPUT_MD_KEY1, OUTPUT_MD_KEY2]:
        res = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=output_key)
        assert res["Body"].read() == expected

def test_cli_build_units_of_work_fail():
    args = CliDocgenArguement(
        subcommand="docgen",
        format="markdown",
        source="not-exist-source",
        dest=f"s3://{TEST_BUCKET_NAME}/{OUTPUT_ROOT_PREFIX}",
    )
    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 1
    assert "[ERROR] failed to setup pairs of template sources and document dests" in result.output


def test_cli_continue():
    
    # temporary replace template source with invalid one
    try:
        with open(INPUT_FILE1, "wb") as fp:
            fp.write(b"invalid")
        args = CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_ROOT_DIR,
            dest=OUTPUT_ROOT_DIR,
            debug=False,
        )
        runner = CliRunner()
        result = runner.invoke(main, args=args.as_list())
        assert result.exit_code == 0
        assert f"[WARNING] failed to generate document [{OUTPUT_MD_FILE1}] from template [{INPUT_FILE1}]" in result.output
        assert f"[INFO] successfully generate document [{OUTPUT_MD_FILE2}] from template [{INPUT_FILE2}]" in result.output

    finally:
        shutil.copy(INPUT_MASTER_FILE, INPUT_FILE1)


@pytest.mark.parametrize("resource_type,document_url", [
    ("AWS::EC2::Instance", "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html"),
    ("Custom::Resource", "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html"),
])
def test_cli_skelton(
    resource_type:str, document_url:Optional[str],
    caplog:pytest.LogCaptureFixture
):
    caplog.set_level(logging.INFO)

    args = CliSkeltonArguement(
        subcommand="skelton",
        type=resource_type,
        format="json",
        custom_resource_specification=CUSTOM_RESOURCE_SPECIFICATION,
    )

    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0
    _ = CfnTemplateResourceDefinition(**json.loads("\n".join(result.stdout.split("\n")[:-2])))

    expected = f"for more information about [{resource_type}], see [{document_url}]"
    assert expected in [r.message for r in caplog.records]

def test_cli_skelton_error(
    caplog:pytest.LogCaptureFixture
):
    caplog.set_level(logging.INFO)

    args = CliSkeltonArguement(
        subcommand="skelton",
        type="Custom::NotExist",
        custom_resource_specification=CUSTOM_RESOURCE_SPECIFICATION,
    )

    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 1

    expected = "skelton for [Custom::NotExist] failed to be shown"
    assert expected in [r.message for r in caplog.records]

def test_cli_skelton_list():

    args = CliSkeltonArguement(
        subcommand="skelton",
        list=True,
        custom_resource_specification=CUSTOM_RESOURCE_SPECIFICATION
    )

    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    assert "AWS::EC2::Instance" in result.stdout
    assert "Custom::Resource" in result.stdout
