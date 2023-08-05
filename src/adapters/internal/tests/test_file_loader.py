import os
import pytest

from src.adapters.internal.file_loader import LocalFileLoader, RemoteFileLoader, get_file_loader

@pytest.fixture
def input_yaml_file():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "docs", "sample-template.yaml"
    )
@pytest.fixture
def input_json_file():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "docs", "sample-template.json"
    )

@pytest.fixture
def http_json_file():
    return "https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"


def test_load_yaml_file(input_yaml_file:str):
    loader = LocalFileLoader(input_yaml_file)
    body = loader.load()
    assert body.startswith("{") and body.endswith("}")

def test_load_json_file(input_json_file:str):
    loader = LocalFileLoader(input_json_file)
    body = loader.load()
    assert body.startswith("{") and body.endswith("}")


def test_load_remote_file_success(http_json_file:str):
    loader = RemoteFileLoader(http_json_file)
    body = loader.load()
    assert body.startswith("{") and body.endswith("}")

def test_load_remote_file_fail(input_yaml_file:str):
    with pytest.raises(AssertionError) as ex:
        _ = RemoteFileLoader(input_yaml_file)
    assert "filepath must be a form of https url" in ex.value.args[0]

@pytest.mark.parametrize("filepath", [
        ("~/file/path"), ("/file/path"), ("./file/path"), ("filepath"),
        ("~\\file\\path"), ("C:\\file\\path"), (".\\file\\path"), 
])
def test_get_local_file_loader(filepath:str):
    file_loader = get_file_loader(filepath)
    assert isinstance(file_loader, LocalFileLoader), type(file_loader)

def test_get_remote_file_loader():
    file_loader = get_file_loader("https://example.com/file")
    assert isinstance(file_loader, RemoteFileLoader), type(file_loader)