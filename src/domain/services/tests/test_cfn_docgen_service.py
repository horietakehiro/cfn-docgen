import os
from typing import Any

import boto3
from adapters.cfn_document_storage import document_storage_facotory
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.cfn_template_provider import template_provider_factory
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig
from domain.model.cfn_document_generator import CfnDocumentDestination, document_generator_factory
from domain.model.cfn_template import CfnTemplateSource
from domain.services.cfn_docgen_service import CfnDocgenService, CfnDocgenServiceCommandInput

INPUT_FILE=os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "docs", "sample-template.yaml",
)
OUTPUT_FILE=os.path.abspath(os.path.join(".", "output.md"))
EXAMPLE_FILE=os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "docs", "sample-template.md",
)
TEST_BUCKET_NAME=os.environ["TEST_BUCKET_NAME"]
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

def teardown_function(function:Any):
    try:
        os.remove(OUTPUT_FILE)
    except FileNotFoundError:
        pass

def test_CfnDocgenService_main_localfile():
    service = CfnDocgenService(
        cfn_template_provider_facotry=template_provider_factory,
        cfn_document_generator_factory=document_generator_factory,
        cfn_document_storage_factory=document_storage_facotory,
        cfn_specification_repository=CfnSpecificationRepository(
            source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
            loader=RemoteFileLoader(),
            cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
            recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        )

    )
    command_input = CfnDocgenServiceCommandInput(
        template_source=CfnTemplateSource(source=INPUT_FILE),
        document_dest=CfnDocumentDestination(OUTPUT_FILE),
        fmt="markdown",
    )
    command_output = service.main(command_input=command_input)
    
    assert command_output.document_dest == OUTPUT_FILE

    with open(OUTPUT_FILE, "r") as ofp:
        with open(EXAMPLE_FILE, "r") as efp:
            output = ofp.read()
            expected = efp.read()

    assert output == expected

    
def test_CfnDocgenService_main_s3obj():
    s3.upload_file(
        Bucket=TEST_BUCKET_NAME,
        Key=TEST_INPUT_KEY,
        Filename=INPUT_FILE,
    )
    service = CfnDocgenService(
        cfn_template_provider_facotry=template_provider_factory,
        cfn_document_generator_factory=document_generator_factory,
        cfn_document_storage_factory=document_storage_facotory,
        cfn_specification_repository=CfnSpecificationRepository(
            source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
            loader=RemoteFileLoader(),
            cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
            recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        )

    )
    command_input = CfnDocgenServiceCommandInput(
        template_source=CfnTemplateSource(source=f"s3://{TEST_BUCKET_NAME}/{TEST_INPUT_KEY}"),
        document_dest=CfnDocumentDestination(dest=f"s3://{TEST_BUCKET_NAME}/{TEST_OUTPUT_KEY}"),
        fmt="markdown",
    )
    command_output = service.main(command_input=command_input)
    
    assert command_output.document_dest == f"s3://{TEST_BUCKET_NAME}/{TEST_OUTPUT_KEY}"

    res = s3.get_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OUTPUT_KEY)
    with open(EXAMPLE_FILE, "rb") as fp:
        assert res["Body"].read() == fp.read()

    