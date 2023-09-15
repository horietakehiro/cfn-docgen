import logging
import os
import shutil
from typing import List
import boto3
import pytest
from cfn_docgen.adapters.internal.file_loader import template_loader_factory
from cfn_docgen.config import AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.model.cfn_template import CfnTemplateSource
from cfn_docgen.domain.services.cfn_docgen_service import CfnDocgenServiceCommandInput

from cfn_docgen.entrypoints.cli.model.cli_model import CfnDocgenCLIUnitsOfWork, CliDocgenArguement

INPUT_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "..", "docs", "sample-template.yaml"
)
EXPECTED_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "..", "docs", "sample-template.md"
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

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),

    )

@pytest.mark.parametrize("case,args,expected", [
    (
        "local source file and local dest file",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_FILE1,
            dest=OUTPUT_MD_FILE1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            )
        ]
    ),
    (
        "local source file and local dest dir",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_FILE1,
            dest=OUTPUT_DIR1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            )
        ]
    ),
    (
        "local source file and s3 dest key",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_FILE1,
            dest=OUTPUT_MD_KEY1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            )
        ]
    ),
    (
        "local source file and s3 dest prefix",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_FILE1,
            dest=OUTPUT_PREFIX1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            )
        ]
    ),
    (
        "local source dir and local dest dir ",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_ROOT_DIR,
            dest=OUTPUT_ROOT_DIR,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "local source dir and s3 dest prefix", 
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_ROOT_DIR,
            dest=OUTPUT_ROOT_PREFIX,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "s3 source key and local dest file",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_KEY1,
            dest=OUTPUT_MD_FILE1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "s3 source key and local dest dir",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_KEY1,
            dest=OUTPUT_DIR1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "s3 source key and s3 dest key",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_KEY1,
            dest=OUTPUT_MD_KEY1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "s3 source key and s3 dest prefix",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_KEY1,
            dest=OUTPUT_PREFIX1,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "s3 source prefix and local dest dir",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_ROOT_PREFIX,
            dest=OUTPUT_ROOT_DIR,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_FILE1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),
    (
        "s3 source prefix and s3 dest prefix",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_ROOT_PREFIX,
            dest=OUTPUT_ROOT_PREFIX,
        ),
        [
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY2, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
            CfnDocgenServiceCommandInput(
                template_source=CfnTemplateSource(INPUT_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                document_dest=CfnDocumentDestination(OUTPUT_MD_KEY1, context=AppContext(
                    log_level=logging.DEBUG,
                    connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
                )),
                fmt="markdown",
            ),
        ]
    ),

])
def test_CfnDocgenCLIUnitsOfWork_build_units_of_work_valid_pattern(
    case:str, # type: ignore
    args:CliDocgenArguement,
    expected:List[CfnDocgenServiceCommandInput],
    context:AppContext,
):
    
    units_of_work = CfnDocgenCLIUnitsOfWork(
        args=args,
        file_loader_factory=template_loader_factory,
        context=context
    )

    assert len(units_of_work.units_of_work) == len(expected)
    for u, e in zip(units_of_work.provide(), expected):
        assert u.template_source.source == e.template_source.source
        assert u.document_dest.dest == e.document_dest.dest

@pytest.mark.parametrize("case,args", [
    (
        "local source dir and local dest file",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_DIR1,
            dest=OUTPUT_MD_FILE1,
        ),
    ),
    (
        "local source dir and s3 dest key",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_DIR1,
            dest=OUTPUT_MD_KEY1,
        ),
    ),
    (
        "s3 source prefix and local dest file",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_PREFIX1,
            dest=OUTPUT_MD_FILE1,
        ),
    ),
    (
        "s3 source prefix and s3 dest key",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source=INPUT_PREFIX1,
            dest=OUTPUT_MD_KEY1,
        ),
    ),
])
def test_CfnDocgenCLIUnitsOfWork_build_units_of_work_invalid_pattern(
    case:str,
    args:CliDocgenArguement,
    context:AppContext,
    caplog:pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    
    with pytest.raises(
        AssertionError,
        match="no valid template sources and document dests are provided"
    ):
        CfnDocgenCLIUnitsOfWork(
            args=args,
            file_loader_factory=template_loader_factory,
            context=context
        )
    
    error_msg = f"invalid arguement pattern: source {args.source} is a directory, while dest {args.dest} is a single file"
    assert error_msg in context.log_messages.as_string(logging.ERROR)
    assert caplog.records[0].message == error_msg


@pytest.mark.parametrize("case,args", [
    (
        "not exist template source",
        CliDocgenArguement(
            subcommand="docgen",
            format="markdown",
            source="not-exist-source",
            dest=OUTPUT_MD_FILE1,
        ),
    ),
])
def test_CfnDocgenCLIUnitsOfWork_build_units_of_work_not_exist_source(
    case:str,
    args:CliDocgenArguement,
    context:AppContext,
    caplog:pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    
    with pytest.raises(
        AssertionError,
        match="no valid template sources and document dests are provided"
    ):
        CfnDocgenCLIUnitsOfWork(
            args=args,
            file_loader_factory=template_loader_factory,
            context=context
        )
    
    error_msg =  f"failed to list template sources at [{args.source}]"
    assert error_msg in context.log_messages.as_string(logging.ERROR)
    assert caplog.records[0].message == error_msg and caplog.records[0].funcName == "build_units_of_work"


