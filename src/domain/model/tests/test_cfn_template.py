from __future__ import annotations
from src.domain.model.cfn_template import (
    CfnTemplateMetadataDefinition,
    CfnTemplateMetadataInterface,
    CfnTemplateMetadataParameterGroup,
    CfnTemplateMetadataParameterGroupLabel,
    CfnTemplateParameter,
    CfnTemplateParameterDefinition
)


def test_CfnTemplateParameter_get_parameter_group():
    parameter_name = "test-param"
    parameter_group = "Group1"
    parameter_definition = CfnTemplateParameterDefinition(
        Type="String"
    )
    metadata = CfnTemplateMetadataDefinition(**{
        "AWS::CloudFormation::Interface": CfnTemplateMetadataInterface(
            ParameterGroups=[
                CfnTemplateMetadataParameterGroup(
                    Label=CfnTemplateMetadataParameterGroupLabel(default=parameter_group),
                    Parameters=[parameter_name],
                ),
            ],
            ParameterLabels={}
        ),
        "CfnDocgen": None,
    }) # type: ignore

    p = CfnTemplateParameter(
        name=parameter_name, definition=parameter_definition,
        metadata=metadata,
    )
    
    assert p.group is not None and p.group == parameter_group


