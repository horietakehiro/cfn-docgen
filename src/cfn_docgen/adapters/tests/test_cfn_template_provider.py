import logging
import os
import pytest
from cfn_docgen.config import AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_template import CfnTemplateDefinition, CfnTemplateSource
from cfn_docgen.adapters.cfn_template_provider import CfnTemplateProvider
from cfn_docgen.adapters.internal.file_loader import template_loader_factory

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

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
def test_load_yaml_template(input_file:str, context:AppContext):
    provider = CfnTemplateProvider(
        file_loader_factory=template_loader_factory,
        context=context,
    )
    template_definition = provider.load_template(CfnTemplateSource(
        source=input_file,
        context=context,
    ))

    assert isinstance(template_definition, CfnTemplateDefinition)
