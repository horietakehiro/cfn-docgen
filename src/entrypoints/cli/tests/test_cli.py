from typing import Any
import pytest
import os
import shutil
import boto3
from click.testing import CliRunner

from src.entrypoints.cli.main import main
from src.entrypoints.cli.model.cli_model import CliArguement

TEST_BUCKET_NAME=os.environ["TEST_BUCKET_NAME"]

def setup_function(function:Any): # type:ignore

    d = os.path.join(
        os.path.dirname(__file__), "data",
    )
    try:
        shutil.rmtree(d)
    except FileNotFoundError:
        pass
    os.makedirs(d, exist_ok=True)        

INPUT_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "docs", "sample-template.yaml"
)
EXPECTED_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "docs", "sample-template.md"
)


TEST_INPUT_KEY="unit-test/sample-template.yaml"
TEST_OUTPUT_KEY="unit-test/sample-template.md"

s3 = boto3.client("s3") # type: ignore
def setup_module(module:Any):
    for key in [TEST_INPUT_KEY, TEST_OUTPUT_KEY]:
        try:
            s3.delete_object(
                Bucket=TEST_BUCKET_NAME,
                Key=key
            )
        except Exception:
            pass
    s3.upload_file(
        Bucket=TEST_BUCKET_NAME,
        Key=TEST_INPUT_KEY,
        Filename=INPUT_FILE,
    )

@pytest.mark.parametrize("source,dest,expected", [
    (
        INPUT_FILE,
        os.path.join(
            os.path.dirname(__file__),
            "data", "sample-template.md"
        ),
        EXPECTED_FILE,
    ),
])
def test_cli_local_file(source:str, dest:str, expected:str):
    args = CliArguement(
        subcommand="docgen",
        format="markdown",
        source=source,
        dest=dest,
    )
    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    with open(dest, "r", encoding="UTF-8") as fp:
        output = fp.read()
    with open(expected, "r", encoding="UTF-8") as fp:
        example = fp.read()
    
    assert output == example


@pytest.mark.parametrize("source,dest,expected", [
    (
        f"s3://{TEST_BUCKET_NAME}/{TEST_INPUT_KEY}",
        f"s3://{TEST_BUCKET_NAME}/{TEST_OUTPUT_KEY}",
        EXPECTED_FILE,
    )
])
def test_cli_s3_key(source:str, dest:str, expected:str):
    args = CliArguement(
        subcommand="docgen",
        format="markdown",
        source=source,
        dest=dest,
    )
    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    assert result.exit_code == 0

    with open(expected, "rb") as fp:
        example = fp.read()
    res = s3.get_object(
        Bucket=TEST_BUCKET_NAME, Key=TEST_OUTPUT_KEY,
    )
    
    assert res["Body"].read() == example


