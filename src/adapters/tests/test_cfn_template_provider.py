import os
import pytest
from src.adapters.cfn_template_provider import CfnTemplateProvider
from src.adapters.internal.file_loader import LocalFileLoader
@pytest.fixture
def input_yaml_file():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "docs", "sample-template.yaml"
    )
@pytest.fixture
def input_json_file():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "docs", "sample-template.json"
    )


def test_load_yaml_template(input_yaml_file:str):
    provider = CfnTemplateProvider(
        file_loader=LocalFileLoader(filepath=input_yaml_file)
    )
    template = provider.load_template()
    print(template)
    raise NotImplementedError
