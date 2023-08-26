import os
import pytest
from cfn_docgen.domain.model.cfn_template import CfnTemplateDefinition, CfnTemplateSource
from cfn_docgen.adapters.cfn_template_provider import CfnTemplateProvider
from cfn_docgen.adapters.internal.file_loader import file_loader_factory

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

@pytest.mark.parametrize("input_file", [
    (
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "docs", "sample-template.yaml"
        )
    ),
    (
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "docs", "sample-template.json"
        )
    )
])
def test_load_yaml_template(input_file:str):
    provider = CfnTemplateProvider(
        file_loader_factory=file_loader_factory,
    )
    template_definition = provider.load_template(CfnTemplateSource(
        source=input_file,
    ))

    assert isinstance(template_definition, CfnTemplateDefinition)
