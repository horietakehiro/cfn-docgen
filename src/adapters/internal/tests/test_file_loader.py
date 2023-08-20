import json
import os
from typing import Any
from domain.model.cfn_template import CfnTemplateSource

from src.adapters.internal.file_loader import LocalFileLoader, RemoteFileLoader, file_loader_factory


INPUT_FILE="input.json"
OUTPUT_FILE="output.json"
INPUT_URL="https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"

def setup_function(function:Any):
    with open(INPUT_FILE, "w") as fp:
        fp.write(json.dumps(
            {
                "key": "val"
            },
            indent=2,
        ))

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

def test_file_loader_factory_LocalFileLoader():
    source = CfnTemplateSource(
        source=INPUT_FILE,
    )
    loader = file_loader_factory(source)
    assert isinstance(loader, LocalFileLoader)


