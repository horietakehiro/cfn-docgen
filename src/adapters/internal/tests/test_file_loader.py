import os
import pytest

from src.adapters.internal.file_loader import LocalFileLoader

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

def test_load_yaml_file(input_yaml_file:str):
    loader = LocalFileLoader(input_yaml_file)
    body = loader.load()
    assert body.startswith("{") and body.endswith("}")

def test_load_json_file(input_json_file:str):
    loader = LocalFileLoader(input_json_file)
    body = loader.load()
    assert body.startswith("{") and body.endswith("}")
