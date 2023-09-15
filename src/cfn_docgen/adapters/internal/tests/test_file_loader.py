import logging
import os
import shutil
from typing import Any, List
from botocore.exceptions import ProfileNotFound

import boto3
import pytest
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.model.cfn_template import CfnTemplateSource

from cfn_docgen.adapters.internal.file_loader import LocalFileLoader, RemoteFileLoader, S3FileLoader, document_loader_factory, specification_loader_factory, template_loader_factory

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

# http url
INPUT_URL="https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
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


def test_LocalFileLoader_download(context:AppContext):
    loader = LocalFileLoader(context=context)
    body = loader.download(INPUT_FILE1)

    with open(INPUT_MASTER_FILE, "rb") as fp:
        expected = fp.read()
    assert body == expected

def test_LocalFileLoader_upload(context:AppContext):
    loader = LocalFileLoader(context=context)
    with open(EXPECTED_MASTER_FILE, "rb") as fp:
        loader.upload(fp.read(), OUTPUT_MD_FILE1)

    with open(EXPECTED_MASTER_FILE, "r") as fp:
        expected = fp.read()
    with open(OUTPUT_MD_FILE1, "r") as fp:
        assert fp.read() == expected

@pytest.mark.parametrize("source,expected", [
    (
        INPUT_ROOT_DIR,
        [INPUT_FILE1, INPUT_FILE2],
    ),
    (
        INPUT_DIR2,
        [INPUT_FILE2],
    ),
    (
        INPUT_FILE1,
        [INPUT_FILE1],
    ),
])
def test_LocalFileLoader_list(source:str, expected:List[str], context:AppContext):
    loader = LocalFileLoader(context=context)
    files = loader.list(source)

    assert len(files) == len(expected)
    for f in files:
        assert f in expected

def test_RemoteFileLoader_download(context:AppContext):
    loader = RemoteFileLoader(context=context)
    body = loader.download(INPUT_URL)

    assert body.decode()[0] == "{" and body.decode()[-1] == "}"

@pytest.mark.parametrize("source,expected", [
    (
        INPUT_FILE1,
        LocalFileLoader,
    ),
    (
        f"s3://{TEST_BUCKET_NAME}/{INPUT_KEY1}",
        S3FileLoader,
    ),
    (
        AppConfig.DEFAULT_SPECIFICATION_URL,
        RemoteFileLoader,
    )
])
def test_file_loader_factory(source:str, expected:Any, context:AppContext):
    template_source = CfnTemplateSource(
        source=source,
        context=context,
    )
    loader = template_loader_factory(template_source, context=context)
    assert isinstance(loader, expected)

@pytest.mark.parametrize("dest,expected", [
    (
        INPUT_FILE1,
        LocalFileLoader,
    ),
    (
        f"s3://{TEST_BUCKET_NAME}/{INPUT_KEY1}",
        S3FileLoader,
    ),
    (
        AppConfig.DEFAULT_SPECIFICATION_URL,
        RemoteFileLoader,
    )
])
def test_document_loader_factory(dest:str, expected:Any, context:AppContext):
    document_dest = CfnDocumentDestination(
        dest=dest,
        context=context,
    )
    loader = document_loader_factory(document_dest, context=context)
    assert isinstance(loader, expected)

def test_S3Fileloader_download(context:AppContext):
    loader = S3FileLoader(context=context)
    body = loader.download(
        source=f"s3://{TEST_BUCKET_NAME}/{INPUT_KEY1}"
    )
    with open(INPUT_MASTER_FILE, "rb") as fp:
        assert fp.read() == body

def test_S3Fileloader_upload(context:AppContext):
    loader = S3FileLoader(context=context)
    dest = f"s3://{TEST_BUCKET_NAME}/{OUTPUT_MD_KEY1}"
    with open(EXPECTED_MASTER_FILE, "rb") as fp:
        expected = fp.read()
    loader.upload(expected, dest)

    s3 = boto3.client("s3") # type: ignore
    res = s3.get_object(
        Bucket=TEST_BUCKET_NAME,
        Key=OUTPUT_MD_KEY1
    )
    assert res["Body"].read() == expected
@pytest.mark.parametrize("source,expected", [
    (
        INPUT_ROOT_PREFIX,
        [INPUT_KEY1, INPUT_KEY2],
    ),
    (
        INPUT_PREFIX2,
        [INPUT_KEY2],
    ),
    (
        INPUT_KEY1,
        [INPUT_KEY1],
    ),
])
def test_S3Fileloader_list(source:str, expected:List[str], context:AppContext):
    loader = S3FileLoader(context=context)
    keys = loader.list(f"s3://{TEST_BUCKET_NAME}/{source}")

    expected = [f"s3://{TEST_BUCKET_NAME}/{e}" for e in expected]
    assert len(keys) == len(expected)
    for k in keys:
        assert k in expected

def test_S3Fileloader_custom_profile(context:AppContext):
    context.connection_settings = ConnectionSettings(
        aws=AwsConnectionSettings(profile_name="not-exist-profile")
    )
    with pytest.raises(ProfileNotFound):
        S3FileLoader(context=context)


@pytest.mark.parametrize("url,expected", [
    ("http://example.com/fie", RemoteFileLoader),
    ("https://example.com/fie", RemoteFileLoader),
    ("s3://bucket/fie", S3FileLoader),
    ("/dir/file", LocalFileLoader),
])
def test_specification_loader_factory(
    url:str, expected:Any,
    context:AppContext,
):
    loader = specification_loader_factory(
        specification_url=url, context=context,
    )
    assert isinstance(loader, expected)