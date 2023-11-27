from typing import Any, List
from dataclasses import dataclass
from behave import fixture # type: ignore
from behave.fixture import use_fixture_by_tag # type: ignore
import os
import shutil
import boto3
import docker # type: ignore
from docker import DockerClient # type: ignore

INPUT_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "sample-template.yaml"
)
EXPECTED_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "sample-template.md"
)

INPUT_CUSTOM_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "custom-resources.yaml"
)
EXPECTED_CUSTOM_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "custom-resources.md"
)
CUSTOM_RESOURCE_SPECIFICATION=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "custom-specification.json"
)


# local directories and files
ROOT_DIR=os.path.join(os.path.dirname(__file__), "data")
INPUT_ROOT_DIR=os.path.join(ROOT_DIR, "input")
INPUT_DIR1 = os.path.join(INPUT_ROOT_DIR, "dir1")
INPUT_FILE1 = os.path.join(INPUT_DIR1, "sample-template.yaml")
INPUT_DIR2 = os.path.join(INPUT_DIR1, "dir2")
INPUT_FILE2 = os.path.join(INPUT_DIR2, "sample-template.yaml")

OUTPUT_ROOT_DIR=os.path.join(ROOT_DIR, "data", "output")
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

SERVERLESS_BUCKET_NAME=os.environ["SERVERLESS_BUCKET_NAME"]


def setup_local_dirs_and_files():
    # cleanup local dirs
    shutil.rmtree(INPUT_ROOT_DIR, ignore_errors=True)
    shutil.rmtree(OUTPUT_ROOT_DIR, ignore_errors=True)

    # prepare input files and dirs
    os.makedirs(INPUT_DIR2, exist_ok=True)
    shutil.copy(INPUT_MASTER_FILE, INPUT_FILE1)
    shutil.copy(INPUT_MASTER_FILE, INPUT_FILE2)


def setup_s3_bucket_and_keys(
    bucket:str,
    prefixes:List[str],
    keys:List[str],
):
    # cleanup s3 keys
    # for prefix in [INPUT_ROOT_PREFIX, OUTPUT_ROOT_PREFIX]:
    for prefix in prefixes:
        res = s3_client.list_objects(
            Bucket=bucket,
            Prefix=prefix.replace(f"s3://{bucket}/", ""),
        )
        contents = res.get("Contents", None)
        if contents is None or len(contents) == 0: # type: ignore
            continue
        s3_client.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [
                    {"Key": content["Key"]} for content in contents # type: ignore
                ]
            }
        )
    
    # prepare input keys
    # for key in [INPUT_KEY1, INPUT_KEY2]:
    for key in keys:
        s3_client.upload_file(
            Bucket=bucket,
            Key=key.replace(f"s3://{bucket}/", ""),
            Filename=INPUT_MASTER_FILE
        )



@dataclass
class CommandLineToolContext:
    format:str
    source:str
    dest:str
    expected:List[str]
    master:str

@dataclass
class ServerlessContext:
    stack_name: str
    format: str
    source:str
    dest: str
    expected:List[str]
    master:str

@dataclass
class PackageContext:
    format: str
    source: str
    dest: str
    expected: List[str]
    master: str

@dataclass
class DockerContext:
    format: str
    source: str
    dest: str
    expected: List[str]
    master: str
    docker_client:DockerClient

@dataclass
class CustomResourceContext:
    format: str
    source: str
    dest: str
    expected: List[str]
    master: str
    custom_resource: str

@dataclass
class SkeletonContext:
    type: str
    stdout: str


@fixture # type: ignore
def command_line_tool(
    context:CommandLineToolContext, 
    fmt:str, source:str, dest:str, expected:List[str], master:str,
    *args, **kwargs # type: ignore
):
    setup_local_dirs_and_files()
    setup_s3_bucket_and_keys(
        bucket=TEST_BUCKET_NAME,
        prefixes=[INPUT_ROOT_PREFIX, OUTPUT_ROOT_PREFIX],
        keys=[INPUT_KEY1, INPUT_KEY2],
    )

    context.format = fmt
    context.source = source
    context.dest = dest
    context.expected = expected
    context.master = master

    yield context


@fixture # type: ignore
def command_line_tool_with_custom_resources(
    context:CustomResourceContext, 
    fmt:str, source:str, dest:str, expected:List[str], master:str, custom_resource:str,
    *args, **kwargs # type: ignore
):
    setup_local_dirs_and_files()
    shutil.copy(INPUT_CUSTOM_MASTER_FILE, source)
    context.format = fmt
    context.source = source
    context.dest = dest
    context.expected = expected
    context.master = master
    context.custom_resource = custom_resource

    yield context

@fixture # type: ignore
def serverless(
    context:ServerlessContext,
    fmt:str, source:str, dest:str, expected:List[str], master:str,
    *args, **kwargs # type: ignore
):

    context.stack_name = "cfn-docgen-serverless-bdd"
    context.format = fmt
    context.source = source.replace(f"{TEST_BUCKET_NAME}", f"{SERVERLESS_BUCKET_NAME}/templates/bdd-test")
    context.dest = dest.replace(f"{TEST_BUCKET_NAME}", f"{SERVERLESS_BUCKET_NAME}/templates/bdd-test")
    context.expected = [e.replace(f"{TEST_BUCKET_NAME}", f"{SERVERLESS_BUCKET_NAME}/documents/templates/bdd-test").replace("output", "input") for e in expected]
    context.master = master

    setup_s3_bucket_and_keys(
        bucket=SERVERLESS_BUCKET_NAME,
        prefixes=["documents/", "templates/"],
        keys=[context.source],
    )

    yield context


@fixture # type: ignore
def package(
    context:PackageContext, 
    fmt:str, source:str, dest:str, expected:List[str], master:str,
    *args, **kwargs # type: ignore
):
    setup_local_dirs_and_files()

    context.format = fmt
    context.source = source
    context.dest = dest
    context.expected = expected
    context.master = master

    yield context



@fixture # type: ignore
def docker_fixture(
    context:DockerContext, 
    fmt:str, source:str, dest:str, expected:List[str], master:str,
    *args, **kwargs # type: ignore
):
    setup_local_dirs_and_files()

    context.format = fmt
    context.source = source
    context.dest = dest.replace(ROOT_DIR, "")
    context.expected = expected
    context.master = master
    context.docker_client = docker.from_env() # type: ignore

    yield context


@fixture # type: ignore
def cdk_fixture(
    context:DockerContext, 
    fmt:str, source:str, dest:str, expected:List[str], master:str,
    *args, **kwargs # type: ignore
):
    setup_local_dirs_and_files()

    context.format = fmt
    context.source = source
    context.dest = dest
    context.expected = expected
    context.master = master

    yield context

@fixture # type: ignore
def skeleton(
    context:SkeletonContext, 
    *args, **kwargs # type: ignore
):
    context.type = "AWS::EC2::Instance"


fixture_registry = { # type: ignore
    "fixture.command_line_tool.markdown.local_single_file_local_single_dest": (
        command_line_tool, 
        ["markdown", INPUT_FILE1, OUTPUT_MD_FILE1, [OUTPUT_MD_FILE1], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.command_line_tool.markdown.local_multiple_source_local_multiple_dest": (
        command_line_tool, 
        ["markdown", INPUT_ROOT_DIR, OUTPUT_ROOT_DIR, [OUTPUT_MD_FILE1, OUTPUT_MD_FILE2], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.command_line_tool.markdown.s3_single_file_s3_single_dest": (
        command_line_tool, 
        ["markdown", INPUT_KEY1, OUTPUT_MD_KEY1, [OUTPUT_MD_KEY1], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.command_line_tool.markdown.s3_multiple_source_s3_multiple_dest": (
        command_line_tool, 
        ["markdown", INPUT_ROOT_PREFIX, OUTPUT_ROOT_PREFIX, [OUTPUT_MD_KEY1, OUTPUT_MD_KEY2], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.command_line_tool.markdown.use_custom_resource_specification": (
        command_line_tool_with_custom_resources, 
        ["markdown", INPUT_FILE1, OUTPUT_MD_FILE1, [OUTPUT_MD_FILE1], EXPECTED_CUSTOM_MASTER_FILE, CUSTOM_RESOURCE_SPECIFICATION],
        {},
    ),
    "fixture.serverless.markdown.s3_single_source_s3_single_dest": (
        serverless,
        ["markdown", INPUT_KEY1, OUTPUT_MD_KEY1, [OUTPUT_MD_KEY1], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.package.markdown.local_single_file_local_single_dest": (
        package, 
        ["markdown", INPUT_FILE1, OUTPUT_MD_FILE1, [OUTPUT_MD_FILE1], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.docker.markdown.local_single_file_local_single_dest": (
        docker_fixture, 
        ["markdown", INPUT_KEY1, OUTPUT_MD_KEY1, [OUTPUT_MD_KEY1], EXPECTED_MASTER_FILE],
        # ["markdown", "/tmp/sample-template.yaml", "/out/sample-template.md", ["/tmp/cfn-docgen-test/sample-template.md"], EXPECTED_MASTER_FILE],
        {},
    ),
    "fixture.cdk.markdown": (
        cdk_fixture, 
        [
            "markdown", 
            os.path.join(os.path.dirname(__file__), "..", "..", "cdk.out", "CfnDocgenSampleCdkStack.template.json"), 
            os.path.join(os.path.dirname(__file__), "..", "..", "docs", "CfnDocgenSampleCdkStack.template.md"), 
            [], 
            EXPECTED_MASTER_FILE
        ],
        {},
    ),
    "fixture.command_line_tool.skeleton.resource_type": (
        skeleton, 
        [],
        {},
    ),

    
} # type: ignore

def before_tag(context:Any, tag:str): # type: ignore
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry) # type: ignore