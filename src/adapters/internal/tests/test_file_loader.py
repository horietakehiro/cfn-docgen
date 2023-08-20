import json
import os
from typing import Any

import boto3
import pytest
from config import AppConfig
from domain.model.cfn_document_generator import CfnDocumentDestination
from domain.model.cfn_template import CfnTemplateSource

from src.adapters.internal.file_loader import LocalFileLoader, RemoteFileLoader, S3FileLoader, document_loader_factory, file_loader_factory


INPUT_FILE=os.path.join(os.path.dirname(__file__), "input.json")
OUTPUT_FILE=os.path.join(os.path.dirname(__file__), "output.json")
INPUT_URL="https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"
TEST_BUCKET_NAME=os.environ["TEST_BUCKET_NAME"]

S3_INPUT_KEY=f"unit-test/input.json"

def setup_function(function:Any):
    with open(INPUT_FILE, "w") as fp:
        fp.write(json.dumps(
            {
                "key": "val"
            },
            indent=2,
        ))

    client = boto3.client("s3") # type: ignore
    client.upload_file(
        Bucket=TEST_BUCKET_NAME,
        Key=S3_INPUT_KEY,
        Filename=INPUT_FILE,
    )

def teardown_function(function:Any):
    try:
        os.remove(INPUT_FILE)
    except FileNotFoundError:
        pass
    try:
        os.remove(OUTPUT_FILE)
    except FileNotFoundError:
        pass

def test_LocalFileLoader_download():
    loader = LocalFileLoader()
    body = loader.download(INPUT_FILE)

    assert json.loads(body.decode())["key"] == "val"


def test_LocalFileLoader_upload():
    loader = LocalFileLoader()
    loader.upload("output".encode(), OUTPUT_FILE)

    with open(OUTPUT_FILE, "r") as fp:
        assert fp.read() == "output"

def test_RemoteFileLoader_download():
    loader = RemoteFileLoader()
    body = loader.download(INPUT_URL)

    assert body.decode()[0] == "{" and body.decode()[-1] == "}"

@pytest.mark.parametrize("source,expected", [
    (
        INPUT_FILE,
        LocalFileLoader,
    ),
    (
        f"s3://{TEST_BUCKET_NAME}/{S3_INPUT_KEY}",
        S3FileLoader,
    ),
    (
        AppConfig.DEFAULT_SPECIFICATION_URL,
        RemoteFileLoader,
    )
])
def test_file_loader_factory(source:str, expected:Any):
    template_source = CfnTemplateSource(
        source=source,
    )
    loader = file_loader_factory(template_source)
    assert isinstance(loader, expected)

@pytest.mark.parametrize("dest,expected", [
    (
        INPUT_FILE,
        LocalFileLoader,
    ),
    (
        f"s3://{TEST_BUCKET_NAME}/{S3_INPUT_KEY}",
        S3FileLoader,
    ),
    (
        AppConfig.DEFAULT_SPECIFICATION_URL,
        RemoteFileLoader,
    )
])
def test_document_loader_factory(dest:str, expected:Any):
    document_dest = CfnDocumentDestination(
        dest=dest,
    )
    loader = document_loader_factory(document_dest)
    assert isinstance(loader, expected)

def test_S3Fileloader_download():
    loader = S3FileLoader()
    body = loader.download(
        source=f"s3://{TEST_BUCKET_NAME}/{S3_INPUT_KEY}"
    )
    with open(INPUT_FILE, "rb") as fp:
        assert fp.read() == body

def test_S3Fileloader_upload():
    loader = S3FileLoader()
    dest = f"s3://{TEST_BUCKET_NAME}/{S3_INPUT_KEY}"
    with open(INPUT_FILE, "rb") as fp:
        expected = fp.read()
    loader.upload(expected, dest)

    s3 = boto3.client("s3") # type: ignore
    res = s3.get_object(
        Bucket=TEST_BUCKET_NAME,
        Key=S3_INPUT_KEY
    )
    assert res["Body"].read() == expected