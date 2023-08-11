from __future__ import annotations
from typing import cast

import pytest
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import  RemoteFileLoader
from config import AppConfig
from src.domain.model.cfn_template import (
    CfnTemplateCondition,
    CfnTemplateMapping,
    CfnTemplateMetadataCfnDocgenDefinition,
    CfnTemplateMetadataDefinition,
    CfnTemplateMetadataInterface,
    CfnTemplateMetadataParameterGroup,
    CfnTemplateMetadataParameterGroupLabel,
    CfnTemplateParameter,
    CfnTemplateParameterDefinition,
    CfnTemplateResourceChildProperty,
    CfnTemplateResourceDefinition,
    CfnTemplateResourceMetadataCfnDocgenDefinition,
    CfnTemplateResourceMetadataDefinition,
    CfnTemplateRule,
    CfnTemplateRuleAssertDefinition,
    CfnTemplateRuleDefinition
)

def test_CfnTemplateResourceDefinition_get_description_for_property():
    prop_type = "CpuOptions"
    prop_name = "CoreCount"
    description = "some-description"
    definition = CfnTemplateResourceDefinition(
        Type="AWS::EC2::Instance",
        Metadata=CfnTemplateResourceMetadataDefinition(
            CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                Properties={
                    prop_type: {
                        prop_name: description
                    }
                }
                
            )
        ),
        Properties={}
    )
    json_path = f"$.{prop_type}.{prop_name}"
    d= definition.get_description_for_property(json_path)
    assert d is not None and d == description


def test_CfnTemplateResourceDefinition_get_definition_for_property():
    prop_type = "CpuOptions"
    prop_name = "CoreCount"
    definition = CfnTemplateResourceDefinition(
        Type="AWS::EC2::Instance",
        Metadata=None, 
        Properties={
            prop_type: {
                prop_name: 10
            }
        }
    )
    json_path = f"$.{prop_type}.{prop_name}"
    d= definition.get_definition_for_property(json_path)
    assert d is not None and d == 10


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


def test_CfnTemplateParameter_get_parameter_group_not_found():
    param_name = "test-param"
    param_def = CfnTemplateParameterDefinition(
        Type="String"
    )
    p = CfnTemplateParameter(
        name=param_name, definition=param_def, metadata=None
    )

    assert p.group is None

def test_CfnTemplateMapping_get_description():
    name = "Map1"
    map_def = {
        "Nam1": {
            "Key1": "Val1",
            "Key2": "Val2"
        },
        "Name2": {
            "Key1": "Val1",
            "Key2": "Val2"
        }
    }
    description = "some description"
    metadata = CfnTemplateMetadataDefinition(
        CfnDocgen=CfnTemplateMetadataCfnDocgenDefinition(
        Mappings={
            name: description
        }
        )
    )
    m = CfnTemplateMapping(name, map_def, metadata)

    assert description == m.description


def test_CfnTemplateMapping_get_description_not_found():
    name = "Map1"
    map_def = {
        "Nam1": {
            "Key1": "Val1",
            "Key2": "Val2"
        },
        "Name2": {
            "Key1": "Val1",
            "Key2": "Val2"
        }
    }
    description = "some description"
    metadata = CfnTemplateMetadataDefinition(
        CfnDocgen=CfnTemplateMetadataCfnDocgenDefinition(
        Mappings={
            "NotExistMap": description
        }
        )
    )
    m = CfnTemplateMapping(name, map_def, metadata)
    assert m.description is None

def test_CfnTemplateCondition_get_description():
    name = "Cond1"
    cond = {
        "Fn::Equals": [
            "hoge", "fuga"
        ]
    }
    description = "some description"

    metadata = CfnTemplateMetadataDefinition(
        CfnDocgen=CfnTemplateMetadataCfnDocgenDefinition(
                Conditions={
                    name: description
                }
        )
    )
    c = CfnTemplateCondition(
        name, cond, metadata
    )

    assert description == c.description

def test_CfnTemplateCondition_get_description_not_found():
    name = "Cond1"
    cond = {
        "Fn::Equals": [
            "hoge", "fuga"
        ]
    }
    metadata = CfnTemplateMetadataDefinition(
        CfnDocgen=CfnTemplateMetadataCfnDocgenDefinition(
                Conditions={
                    "NotEixstCond": "some-descirption"
                }
        )
    )
    c = CfnTemplateCondition(
        name, cond, metadata
    )
    assert c.description is None

def test_CfnTemplateRule_get_description():
    name = "rule1"
    rule = CfnTemplateRuleDefinition(
        RuleCondition=None,
        Assertions=[
            CfnTemplateRuleAssertDefinition(
                Assert={"hoge": "fuga"},
                AssertDescription="hogefuga"
            )
        ]
    )
    description = "some-descritpion"

    metadata = CfnTemplateMetadataDefinition(
        CfnDocgen=CfnTemplateMetadataCfnDocgenDefinition(
        Rules={name: description}
        )
    )

    r = CfnTemplateRule(
        name, rule, metadata
    )

    assert description == r.description


def test_CfnTemplateRule_get_description_not_found():
    name = "rule1"
    rule = CfnTemplateRuleDefinition(
        RuleCondition=None,
        Assertions=[
            CfnTemplateRuleAssertDefinition(
                Assert={"hoge": "fuga"},
                AssertDescription="hogefuga"
            )
        ]
    )
    description = "some-descritpion"
    metadata = CfnTemplateMetadataDefinition(
        CfnDocgen=CfnTemplateMetadataCfnDocgenDefinition(
        Rules={"NotExistRule": description}
        )
    )

    r = CfnTemplateRule(
        name, rule, metadata
    )

    assert r.description is None


@pytest.fixture
def spec_repository():
    return CfnSpecificationRepository(
        loader=RemoteFileLoader("https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"),
        cache=LocalFileCache(AppConfig())
    )

def test_CfnTemplateResourceChildProperty_PrimitiveType(spec_repository:CfnSpecificationRepository):
    description = "some-description"
    prop_name = "CoreCount"
    prop_type = "CpuOptions"
    resource_type = "AWS::EC2::Instance"
    specs = spec_repository.get_specs_for_resource(resource_type)
    parent_path = f"$.{prop_type}"
    definition = 10

    p = CfnTemplateResourceChildProperty(
        prop_name=prop_name,
        prop_type=prop_type,
        resource_definition=CfnTemplateResourceDefinition(
            Metadata=CfnTemplateResourceMetadataDefinition(
                CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                    Properties={
                        prop_type: {
                            prop_name: description
                        }
                    }
                )
            ),
            Type=resource_type,
            Properties={
                prop_type: {
                    prop_name: definition
                }
            }
        ),
        specs=specs,
        parent_path=parent_path,
        index=None,
        depth=1
    )

    assert p.json_path == f"{parent_path}.{prop_name}"
    assert p.description == description
    assert p.definition is not None and p.definition == definition
    assert (
        p.primitive_spec is not None and p.primitive_spec.PrimitiveType == "Integer"
    )
    assert len(p.properties) == 0


def test_CfnTemplateResourceChildProperty_PrimitiveItemType(spec_repository:CfnSpecificationRepository):
    description = "some-description"
    prop_name = "GroupSet"
    prop_type = "NetworkInterface"
    resource_type = "AWS::EC2::Instance"
    specs = spec_repository.get_specs_for_resource(resource_type)
    parent_path = f"$.{prop_type}"
    definition = [
        "group1", "group2"
    ]

    p = CfnTemplateResourceChildProperty(
        prop_name=prop_name,
        prop_type=prop_type,
        resource_definition=CfnTemplateResourceDefinition(
            Metadata=CfnTemplateResourceMetadataDefinition(
                CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                    Properties={
                        prop_type: {
                            prop_name: description
                        }
                    }
                )
            ),
            Type=resource_type,
            Properties={
                prop_type: {
                    prop_name: definition
                }
            }
        ),
        specs=specs,
        parent_path=parent_path,
        index=None,
        depth=1
    )

    assert p.json_path == f"{parent_path}.{prop_name}"
    assert p.description == description
    assert (
        p.definition is not None
        and all([pd == ed for pd, ed in zip(cast(list, p.definition), definition)])) # type:ignore
    assert (
        p.primitive_spec is not None 
        and p.primitive_spec.PrimitiveItemType == "String"
        and p.primitive_spec.Type == "List"
    )
    assert len(p.properties) == 0


def test_CfnTemplateResourceChildProperty_Type(spec_repository:CfnSpecificationRepository):
    description = "some-description"
    prop_name = "Ebs"
    prop_type = "Ebs"
    resource_type = "AWS::EC2::Instance"
    specs = spec_repository.get_specs_for_resource(resource_type)
    parent_path = "$.BlockDeviceMappings"
    definition = {
        "Encrypted" : True,
    }


    p = CfnTemplateResourceChildProperty(
        prop_name=prop_name,
        prop_type=prop_type,
        resource_definition=CfnTemplateResourceDefinition(
            Metadata=CfnTemplateResourceMetadataDefinition(
                CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                    Properties={
                        "BlockDeviceMappings": [
                            {
                                prop_name: description
                            }

                        ]
                    }
                )
            ),
            Type=resource_type,
            Properties={
                "BlockDeviceMappings": [
                    {
                        prop_name: definition
                    }
                ]
            }
        ),
        specs=specs,
        parent_path=parent_path,
        index=0,
        depth=1
    )

    print(p.__dict__)
    assert p.json_path == f"{parent_path}[0].{prop_name}"
    assert p.description == description
    assert p.definition is not None
    print(specs.PropertySpecs[f"{resource_type}.{prop_name}"].Properties)
    assert p.property_spec is not None 
    assert p.type == "Ebs"
    assert len(p.properties) == 7
    encrypted_prop = [prop for prop in p.properties if prop.name == "Encrypted"]
    assert len(encrypted_prop) == 1 and encrypted_prop[0].definition == True

