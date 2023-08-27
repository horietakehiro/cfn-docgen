# type: ignore
from typing import Any
from dataclasses import dataclass
from behave import fixture
from behave.fixture import use_fixture_by_tag
import os
import shutil
import boto3
BEHAVE_DEBUG_ON_ERROR = True


INPUT_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "sample-template.yaml"
)
EXPECTED_MASTER_FILE=os.path.join(
    os.path.dirname(__file__),
    "..", "..", "docs", "sample-template.md"
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

def setup_local_dirs_and_files():
    # cleanup local dirs
    shutil.rmtree(INPUT_ROOT_DIR, ignore_errors=True)
    shutil.rmtree(OUTPUT_ROOT_DIR, ignore_errors=True)

    # prepare input files and dirs
    os.makedirs(INPUT_DIR2, exist_ok=True)
    shutil.copy(INPUT_MASTER_FILE, INPUT_FILE1)
    shutil.copy(INPUT_MASTER_FILE, INPUT_FILE2)


def setup_s3_bucket_and_keys():
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



@dataclass
class CommandLineToolContext:
    format:str
    source:str
    dest:str
    expected:str

@fixture
def command_line_tool(
    context:CommandLineToolContext, 
    # fmt:str, source:str, dest:str, 
    *args, **kwargs
):
    # setup_local_dirs_and_files()
    print("hogeufga")

    # context.format = fmt
    # context.source = source
    # context.dest = dest
    # context.expected = EXPECTED_MASTER_FILE

    yield context


fixture_registry = {
    "fixture.command_line_tool.markdown.local_single_file_local_single_dest": (
        command_line_tool, 
        # ["markdown", INPUT_FILE1, OUTPUT_MD_FILE1], 
        {},
    )
}

def before_tag(context:Any, tag:str):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry)