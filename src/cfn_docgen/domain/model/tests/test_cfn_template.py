from __future__ import annotations
import logging
from typing import Any, Mapping, Optional, cast, List

import pytest
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationResourceTypeName
from cfn_docgen.domain.model.cfn_template import (
    CfnTemplateConditionsNode,
    CfnTemplateDefinition,
    CfnTemplateMappingsNode,
    CfnTemplateMetadataCfnDocgenDefinition,
    CfnTemplateMetadataDefinition,
    CfnTemplateMetadataInterface,
    CfnTemplateMetadataParameterGroup,
    CfnTemplateMetadataParameterGroupLabel,
    CfnTemplateOutputDefinition,
    CfnTemplateOutputsNode,
    CfnTemplateParameterDefinition,
    CfnTemplateParametersNode,
    CfnTemplateResourceDefinition,
    CfnTemplateResourceMetadataCfnDocgenDefinition,
    CfnTemplateResourceMetadataDefinition,
    CfnTemplateResourceNode,
    CfnTemplateResourcesNode,
    CfnTemplateRuleAssertDefinition,
    CfnTemplateRuleDefinition,
    CfnTemplateRulesNode,
    CfnTemplateSource,
    CfnTemplateTree,
    ResourceInfo
)

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

def test_CfnTemplateMetadataDefinition_get_resource_description():
    description = "some-description"
    cfn_docgen = CfnTemplateResourceMetadataCfnDocgenDefinition(
        Description=description
    )

    d = cfn_docgen.get_resource_description()
    assert d is not None and d == description

@pytest.mark.parametrize("definition", [
    (CfnTemplateResourceMetadataCfnDocgenDefinition())

])
def CfnTemplateResourceMetadataCfnDocgenDefinition_get_resource_description_none(cfn_docgen:CfnTemplateResourceMetadataCfnDocgenDefinition):
    assert cfn_docgen.get_resource_description() is None

@pytest.mark.parametrize("json_path,expected,", [
    ("$.ImageId", "imageid"),
    ("$.CpuOptions.CoreCount", "corecount"),
    ("$.BlockDeviceMappings", None),
    ("$.BlockDeviceMappings[1].Ebs.VolumeType", "volumetype"),
    ("$.Tags", "tags"),
    ("$.NotExist", None),
])
def test_CfnTemplateResourceMetadataCfnDocgenDefinition_get_property_description_by_json_path(
    json_path:str, expected:Optional[str],
):
    definition = CfnTemplateResourceMetadataCfnDocgenDefinition(
        Properties={
            "ImageId": "imageid",
            "CpuOptions": {
                "CoreCount": "corecount"
            },
            "BlockDeviceMappings": [
                {},
                {
                    "Ebs": {
                        "VolumeType": "volumetype"
                    }
                }
            ],
            "Tags": "tags"
        }
    )
    d = definition.get_property_description_by_json_path(json_path)
    if expected is None:
        assert d is None
    else:
        assert d == expected





def test_CfnTemplateParametersNode(context:AppContext):
    parameter_definitions:Mapping[str, CfnTemplateParameterDefinition] = {
        "param11": CfnTemplateParameterDefinition(Type="String"),
        "param12": CfnTemplateParameterDefinition(Type="Number"),
        "param21": CfnTemplateParameterDefinition(Type="CommaDelimitedList"),
        "param": CfnTemplateParameterDefinition(Type="AWS::EC2::AvailabilityZone::Name"),
    }
    parameter_groups = [
        CfnTemplateMetadataParameterGroup(
            Label=CfnTemplateMetadataParameterGroupLabel(default="group1"),
            Parameters=["param11", "param12"],
        ),
        CfnTemplateMetadataParameterGroup(
            Label=CfnTemplateMetadataParameterGroupLabel(default="group2"),
            Parameters=["param21"],
        ),
        CfnTemplateMetadataParameterGroup(
            Label=CfnTemplateMetadataParameterGroupLabel(default="group3"),
            Parameters=["param3"],
        ),
    ]
    node = CfnTemplateParametersNode(
        definitions=parameter_definitions,
        parameter_groups=parameter_groups,
        context=context,
    )

    group_node1 = node.group_nodes.get("group1", None)
    group_node2 = node.group_nodes.get("group2", None)
    group_node3 = node.group_nodes.get("group3", None)
    independent_group_node = node.group_nodes.get(CfnTemplateParametersNode.group_name_for_independent_parameters, None)
    assert group_node1 is not None and len(group_node1.leaves.keys()) == 2
    assert group_node2 is not None and len(group_node2.leaves.keys()) == 1
    assert group_node3 is not None and len(group_node3.leaves.keys()) == 0
    assert independent_group_node is not None and len(independent_group_node.leaves.keys()) == 1

    parameter_leaf11 = group_node1.leaves.get("param11", None)
    parameter_leaf12 = group_node1.leaves.get("param12", None)
    parameter_leaf21 = group_node2.leaves.get("param21", None)
    independent_parameter_leaf = independent_group_node.leaves.get("param", None)
    assert parameter_leaf11 is not None and parameter_leaf11.definition.Type == "String"
    assert parameter_leaf12 is not None and parameter_leaf12.definition.Type == "Number"
    assert parameter_leaf21 is not None and parameter_leaf21.definition.Type == "CommaDelimitedList"
    assert independent_parameter_leaf is not None and independent_parameter_leaf.definition.Type == "AWS::EC2::AvailabilityZone::Name"

def test_CfnTemplateMappingsNode(context:AppContext):
    mappings_definition:Mapping[str, Mapping[str, Mapping[str, Any]]] = {
        "map1": {
            "name11": {
                "key111": "value111",
                "key112": "value112"
            },
            "name12": {
                "key121": "value121",
                "key122": "value122"
            }
        },
        "map2": {
            "name21": {
                "key211": "value211",
                "key212": "value212"
            },
            "name22": {
                "key221": "value221",
                "key222": "value222"
            }
        }

    }
    descriptions:Mapping[str, str] = {
        "map1": "description1",
        "map3": "description3"
    }
    node = CfnTemplateMappingsNode(
        definitions=mappings_definition,
        descriptions=descriptions,
        context=context,
    )

    leaf1 = node.mapping_leaves["map1"]
    assert leaf1.definition["name11"]["key111"] == "value111"
    assert leaf1.definition["name12"]["key122"] == "value122"
    assert leaf1.description is not None and leaf1.description == "description1"

    leaf2 = node.mapping_leaves["map2"]
    assert leaf2.definition["name21"]["key211"] == "value211"
    assert leaf2.definition["name22"]["key222"] == "value222"
    assert leaf2.description is None

    with pytest.raises(KeyError):
        node.mapping_leaves["map3"]
    

def test_CfnTemplateRulesNode(context:AppContext):
    rule_definitions:Mapping[str, CfnTemplateRuleDefinition] = {
        "rule1": CfnTemplateRuleDefinition(
            RuleCondition=None,
            Assertions=[
                CfnTemplateRuleAssertDefinition(
                    AssertDescription="assertdescription",
                    Assert={None: None}
                )
            ]
        ),
        "rule2": CfnTemplateRuleDefinition(
            RuleCondition={"rule": "condition"},
            Assertions=[
                CfnTemplateRuleAssertDefinition(
                    Assert={None: None},
                    AssertDescription="assertdescription"
                )
            ]
        )
    }
    descriptions = {
        "rule1": "description1",
        "rule3": "description3"
    }
    node = CfnTemplateRulesNode(
        definitions=rule_definitions,
        descriptions=descriptions,
        context=context,
    )

    leaf1 = node.rule_leaves["rule1"]
    assert leaf1.definition.RuleCondition is None
    assert leaf1.definition.Assertions[0].AssertDescription == "assertdescription"
    assert leaf1.description is not None and leaf1.description == "description1"

    leaf2 = node.rule_leaves["rule2"]
    assert leaf2.definition.RuleCondition is not None and leaf2.definition.RuleCondition["rule"] == "condition"
    assert leaf2.description is None

    with pytest.raises(KeyError):
        node.rule_leaves["rule3"]
    

def test_CfnTemplateConditionsNode(context:AppContext):
    definitions:Mapping[str, Mapping[str, Any]] = {
        "cond1": {
            "key1": "value1"
        },
        "cond2": {
            "key2": "value2"
        }
    }
    description = {
        "cond1": "description1",
        "cond3": "descirption3"
    }
    node = CfnTemplateConditionsNode(
        definitions=definitions,
        descriptions=description,
        context=context,
    )

    leaf1 = node.condition_leaves["cond1"]
    assert leaf1.definition["key1"] == "value1"
    assert leaf1.descirption is not None and leaf1.descirption == "description1"

    leaf2 = node.condition_leaves["cond2"]
    assert leaf2.definition["key2"] == "value2"
    assert leaf2.descirption is None

    with pytest.raises(KeyError):
        node.condition_leaves["cond3"]

def test_CfnTemplateOutputsNode(context:AppContext):
    definitions:Mapping[str, CfnTemplateOutputDefinition] = {
        "out1": CfnTemplateOutputDefinition(
            Description="description1",
            Value="value1"
        ),
        "out2": CfnTemplateOutputDefinition(
            Description=None,
            Value="value2"
        ),
    }

    node = CfnTemplateOutputsNode(
        definitions=definitions,
        context=context,
    )


    leaf1 = node.output_leaves.get("out1")
    assert leaf1 is not None
    leaf2 = node.output_leaves.get("out2")
    assert leaf2 is not None

@pytest.fixture
def spec_repository(context:AppContext):
    return CfnSpecificationRepository(
        context=context,
        source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
    )

def all_resource_types():
    context = AppContext(log_level=logging.DEBUG)
    spec_repository = CfnSpecificationRepository(
        context=context,
        source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
    )
    return list(spec_repository.spec.ResourceTypes.keys())

def test_CfnTemplateResourcesNode_aws_ec2_instance(
    spec_repository:CfnSpecificationRepository,
    context:AppContext,
):
    resource_description = "resource-descirption"
    property_descriptions = {
        "ImageId": "imageid",
        "BlockDeviceMappings": [
            {
                "Ebs": "ebs"
            }
        ],
        "SecurityGroupIds": "securitygroupids",
        "Tags": [
            {},
            {
                "Key": "key"
            }
        ]
    }
    definitions:Mapping[str, CfnTemplateResourceDefinition] = {
        "Instance": CfnTemplateResourceDefinition(
            Type="AWS::EC2::Instance",
            DependsOn=["VPC"],
            DeletionPolicy="Retain",
            Metadata=CfnTemplateResourceMetadataDefinition(
                CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                    Description=resource_description,
                    Properties=property_descriptions,
                )
            ),
            Properties={
                "ImageId": "IMAGEID",
                "BlockDeviceMappings": [
                    {
                        "Ebs": {
                            "Encrypted" : True,
                            "VolumeSize" : 0,
                            "VolumeType" : "VOLUMETYPE"
                        }
                    },
                    {
                        "NoDevice": {} 
                    }
                ],
                "CpuOptions": {
                    "CoreCount": 0
                },
                "SecurityGroupIds": [
                    "SECURITYGROUPID1",
                    "SECURITYGROUPID2",
                    "SECURITYGROUPID3",
                ],
                "Tags": [
                    {
                        "Key": "KEY1",
                        "Value": "VALUE1"
                    },
                    {
                        "Key": "KEY2",
                        "Value": "VALUE2"
                    }
                ]
            }
        )
    }

    resources_node = CfnTemplateResourcesNode(
        definitions=definitions,
        spec_repository=spec_repository,
        context=context,
        resource_groups={},
    )

    instance_node = resources_node.group_nodes[resources_node.group_name_for_independent_resources].resource_nodes.get("Instance")
    assert instance_node is not None
    assert instance_node.description is not None and instance_node.description == resource_description
    assert len(instance_node.depends_on) == 1 and instance_node.depends_on[0] == "VPC"
    assert instance_node.deletion_policy == "Retain"
    assert instance_node.update_policy is None
    assert instance_node.creation_policy is None
    assert instance_node.update_replace_policy == "Delete"
    assert instance_node.spec.Documentation is not None and instance_node.spec.Documentation == "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html"

    properties_node = instance_node.properties_node

    image_id_leaf = properties_node.property_leaves.get("ImageId")
    assert image_id_leaf is not None
    assert image_id_leaf.definition == "IMAGEID"
    assert image_id_leaf.json_path == "$.ImageId"
    assert image_id_leaf.description == "imageid"
    assert image_id_leaf.spec.PrimitiveType is not None and image_id_leaf.spec.PrimitiveType == "String"

    cpu_options_node = properties_node.property_nodes.get("CpuOptions")
    assert cpu_options_node is not None
    assert cpu_options_node.description is None
    assert cpu_options_node.json_path == "$.CpuOptions"
    assert cpu_options_node.spec is not None
    assert cpu_options_node.spec.Type is not None and cpu_options_node.spec.Type == "CpuOptions"
    core_count_leaf = cpu_options_node.property_leaves.get("CoreCount")
    assert core_count_leaf is not None
    assert core_count_leaf.description is None
    assert core_count_leaf.json_path == "$.CpuOptions.CoreCount"
    assert core_count_leaf.spec is not None
    assert core_count_leaf.spec.PrimitiveType is not None and core_count_leaf.spec.PrimitiveType == "Integer"
    assert core_count_leaf.definition is not None and core_count_leaf.definition == 0
    threads_per_core_leaf = cpu_options_node.property_leaves.get("ThreadsPerCore")
    assert threads_per_core_leaf is not None
    assert threads_per_core_leaf.description is None
    assert threads_per_core_leaf.json_path == "$.CpuOptions.ThreadsPerCore"
    assert threads_per_core_leaf.spec is not None
    assert threads_per_core_leaf.spec.PrimitiveType is not None and threads_per_core_leaf.spec.PrimitiveType == "Integer"
    assert threads_per_core_leaf.definition is None

    bdm_nodes = properties_node.property_nodes_list.get("BlockDeviceMappings")
    assert bdm_nodes is not None and len(bdm_nodes) == 2
    first_bdm_node = bdm_nodes[0]
    assert first_bdm_node.description is None
    assert first_bdm_node.json_path == "$.BlockDeviceMappings[0]"
    assert first_bdm_node.spec is not None
    assert first_bdm_node.spec.Type is not None and first_bdm_node.spec.Type == "List"
    assert first_bdm_node.spec.ItemType is not None and first_bdm_node.spec.ItemType == "BlockDeviceMapping"
    ebs_node = first_bdm_node.property_nodes.get("Ebs")
    assert ebs_node is not None
    assert ebs_node.description is not None and ebs_node.description == "ebs"
    assert ebs_node.json_path == "$.BlockDeviceMappings[0].Ebs"
    assert ebs_node.spec is not None
    assert ebs_node.spec.Type is not None and ebs_node.spec.Type == "Ebs"
    encrypted_leaf = ebs_node.property_leaves.get("Encrypted")
    assert encrypted_leaf is not None
    assert encrypted_leaf.description is None
    assert encrypted_leaf.json_path == "$.BlockDeviceMappings[0].Ebs.Encrypted"
    assert encrypted_leaf.spec is not None
    assert encrypted_leaf.spec.PrimitiveType is not None and encrypted_leaf.spec.PrimitiveType == "Boolean"
    assert encrypted_leaf.definition is not None and encrypted_leaf.definition == True
    second_bdm_node = bdm_nodes[1]
    assert second_bdm_node.description is None
    assert second_bdm_node.json_path == "$.BlockDeviceMappings[1]"
    assert second_bdm_node.spec is not None
    assert second_bdm_node.spec.Type is not None and second_bdm_node.spec.Type == "List"
    assert second_bdm_node.spec.ItemType is not None and second_bdm_node.spec.ItemType == "BlockDeviceMapping"
    nodevice_node = second_bdm_node.property_nodes.get("NoDevice")
    assert nodevice_node is not None
    assert nodevice_node.description is None
    assert nodevice_node.json_path == "$.BlockDeviceMappings[1].NoDevice"
    assert nodevice_node.spec is not None
    assert nodevice_node.spec.Type is not None and nodevice_node.spec.Type == "NoDevice"
    assert len(nodevice_node.property_leaves) == 0
    assert len(nodevice_node.property_nodes) == 0
    assert len(nodevice_node.property_nodes_list) == 0
    assert len(nodevice_node.property_nodes_map) == 0
    device_name_leaf = second_bdm_node.property_leaves.get("DeviceName")
    assert device_name_leaf is not None
    assert device_name_leaf.description is None
    assert device_name_leaf.json_path == "$.BlockDeviceMappings[1].DeviceName"
    assert device_name_leaf.spec is not None
    assert device_name_leaf.spec.PrimitiveType is not None and device_name_leaf.spec.PrimitiveType == "String"
    assert device_name_leaf.definition is None

    sg_ids_leaf = properties_node.property_leaves.get("SecurityGroupIds")
    assert sg_ids_leaf is not None
    assert sg_ids_leaf.description is not None and sg_ids_leaf.description == "securitygroupids"
    assert sg_ids_leaf.json_path == "$.SecurityGroupIds"
    assert sg_ids_leaf.spec is not None
    assert sg_ids_leaf.spec.Type is not None and sg_ids_leaf.spec.Type == "List"
    assert sg_ids_leaf.spec.PrimitiveItemType is not None and sg_ids_leaf.spec.PrimitiveItemType == "String"
    assert isinstance(sg_ids_leaf.definition, list)
    assert all([r == e for r, e in zip(sg_ids_leaf.definition, ["SECURITYGROUPID1", "SECURITYGROUPID2"])])

    tags_nodes = properties_node.property_nodes_list.get("Tags")
    assert tags_nodes is not None and len(tags_nodes) == 2, properties_node.property_nodes_list
    first_tag_node = tags_nodes[0]
    assert first_tag_node.description is None
    assert first_tag_node.json_path == "$.Tags[0]"
    assert first_tag_node.spec is not None
    assert first_tag_node.spec.Type is not None and first_tag_node.spec.Type == "List"
    assert first_tag_node.spec.ItemType is not None and first_tag_node.spec.ItemType == "Tag"
    first_key_leaf = first_tag_node.property_leaves.get("Key")
    assert first_key_leaf is not None
    assert first_key_leaf.description is None
    assert first_key_leaf.json_path == "$.Tags[0].Key"
    assert first_key_leaf.spec is not None
    assert first_key_leaf.spec.PrimitiveType is not None and first_key_leaf.spec.PrimitiveType == "String"
    assert first_key_leaf.definition is not None and first_key_leaf.definition == "KEY1"
    first_value_leaf = first_tag_node.property_leaves.get("Value")
    assert first_value_leaf is not None
    assert first_value_leaf.description is None
    assert first_value_leaf.json_path == "$.Tags[0].Value"
    assert first_value_leaf.spec is not None
    assert first_value_leaf.spec.PrimitiveType is not None and first_value_leaf.spec.PrimitiveType == "String"
    assert first_value_leaf.definition is not None and first_value_leaf.definition == "VALUE1"
    second_tag_node = tags_nodes[1]
    assert second_tag_node.description is None
    assert second_tag_node.json_path == "$.Tags[1]"
    assert second_tag_node.spec is not None
    assert second_tag_node.spec.Type is not None and first_tag_node.spec.Type == "List"
    assert second_tag_node.spec.ItemType is not None and first_tag_node.spec.ItemType == "Tag"
    second_key_leaf = second_tag_node.property_leaves.get("Key")
    assert second_key_leaf is not None
    assert second_key_leaf.description is not None and second_key_leaf.description == "key"
    assert second_key_leaf.json_path == "$.Tags[1].Key"
    assert second_key_leaf.spec is not None
    assert second_key_leaf.spec.PrimitiveType is not None and second_key_leaf.spec.PrimitiveType == "String"
    assert second_key_leaf.definition is not None and second_key_leaf.definition == "KEY2"
    second_value_leaf = second_tag_node.property_leaves.get("Value")
    assert second_value_leaf is not None
    assert second_value_leaf.description is None
    assert second_value_leaf.json_path == "$.Tags[1].Value"
    assert second_value_leaf.spec is not None
    assert second_value_leaf.spec.PrimitiveType is not None and first_value_leaf.spec.PrimitiveType == "String"
    assert second_value_leaf.definition is not None and second_value_leaf.definition == "VALUE2"
    

    key_name_node = properties_node.property_leaves.get("KeyName")
    assert key_name_node is not None
    assert key_name_node.description is None
    assert key_name_node.json_path == "$.KeyName"
    assert key_name_node.spec is not None
    assert key_name_node.spec.PrimitiveType is not None and key_name_node.spec.PrimitiveType == "String"
    assert key_name_node.definition is None



# @pytest.mark.skipif(condition=os.environ.get("SKIP_LONG_TEST", False), reason="this test takes long time to run")
# @pytest.mark.parametrize("resource_type", [
#     (r) for r in all_resource_types()
# ])
# def test_CfnTemplateResourcesNode_all_resource_types(
#     resource_type:str, spec_repository:CfnSpecificationRepository,
#     context:AppContext,
# ):
#     definitions:Mapping[str, CfnTemplateResourceDefinition] = {
#         resource_type: CfnTemplateResourceDefinition(
#             Type=resource_type,
#             Properties={}
#         )
#     }

#     resources_node = CfnTemplateResourcesNode(
#         definitions=definitions,
#         spec_repository=spec_repository,
#         context=context,
#         resource_groups={},
#     )

#     resource_node = resources_node.group_nodes[resources_node.group_name_for_independent_resources].resource_nodes.get(resource_type)
#     assert resource_node is not None
#     assert resource_node.spec is not None
#     properties_node = resource_node.properties_node
#     assert (
#         len(properties_node.property_leaves) > 0
#         or len(properties_node.property_nodes) > 0
#         or len(properties_node.property_nodes_list) > 0
#         or len(properties_node.property_nodes_map)> 0
#         # resource types without any properties
#         or resource_type == "AWS::CloudFormation::WaitConditionHandle"
#         or resource_type == "AWS::DevOpsGuru::LogAnomalyDetectionIntegration"
#     )


def test_CfnTemplateResourcesNode_avoid_recursion_error(
    spec_repository:CfnSpecificationRepository,
    context:AppContext,
):
    definitions:Mapping[str, CfnTemplateResourceDefinition] = {
        "WithDefinition": CfnTemplateResourceDefinition(
            Type="AWS::WAFv2::RuleGroup",
            Properties={
                "Rules": [
                    {
                        "Statement": {
                            "AndStatement": {
                                "Statements": [
                                    {
                                        "RateBasedStatement": {
                                            "Limit": 500
                                        },
                                    },
                                    {
                                        "ByteMatchStatement": {
                                            "FieldToMatch": {
                                                "Method": {"Name": "GET"}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
        ),
        "WithoutDefinition": CfnTemplateResourceDefinition(
            Type="AWS::WAFv2::RuleGroup",
            Properties={},
        )
    }

    resources_node = CfnTemplateResourcesNode(
        definitions=definitions,
        spec_repository=spec_repository,
        context=context,
        resource_groups={},
    )
    with_definition_node = resources_node.group_nodes[resources_node.group_name_for_independent_resources].resource_nodes.get("WithDefinition")
    assert with_definition_node is not None
    rules = with_definition_node.properties_node.property_nodes_list.get("Rules")
    assert rules is not None and len(rules) == 1
    statement1 = rules[0].property_nodes.get("Statement")
    assert statement1 is not None
    and_statement = statement1.property_nodes.get("AndStatement")
    assert and_statement is not None
    statements = and_statement.property_nodes_list.get("Statements")
    assert statements is not None and len(statements) == 2
    byte_statement = statements[1].property_nodes.get("ByteMatchStatement")
    assert byte_statement is not None
    field_to_match = byte_statement.property_nodes.get("FieldToMatch")
    assert field_to_match is not None
    method = field_to_match.property_leaves.get("Method")
    assert method is not None and method.definition is not None and cast(Mapping[str, Any], method.definition)["Name"] == "GET"

    without_definition_node = resources_node.group_nodes[resources_node.group_name_for_independent_resources].resource_nodes.get("WithoutDefinition")
    assert without_definition_node is not None
    rules_node = without_definition_node.properties_node.property_nodes_list["Rules"]
    assert len(rules_node) == 0


def test_CfnTemplateTree(
    spec_repository:CfnSpecificationRepository,
    context:AppContext,
):
    definition = CfnTemplateDefinition(
        AWSTemplateFormatVersion="2012-10",
        Description="template-description",
        Metadata=CfnTemplateMetadataDefinition(**{
            'AWS::CloudFormation::Interface': CfnTemplateMetadataInterface(
                ParameterGroups=[
                    CfnTemplateMetadataParameterGroup(
                        Label=CfnTemplateMetadataParameterGroupLabel(
                            default="group1"
                        ),
                        Parameters=["param1"]
                    )
                ]
            ),
            "CfnDocgen": CfnTemplateMetadataCfnDocgenDefinition(
                Description="cfn-docgen-template-description",
                Mappings={
                    "map1": "map1-description"
                },
                Rules={
                    "rule1": "rule1-description"
                },
                Conditions={
                    "cond1": "cond1-description"
                },
            )
        }), # type: ignore
        Parameters={
            "param1": CfnTemplateParameterDefinition(
                Type="String"
            ),
            "param2": CfnTemplateParameterDefinition(
                Type="Number"
            )
        },
        Mappings={
            "map1": {
                "name1": {
                    "key1": "value1"
                }
            }
        },
        Rules={
            "rule1": CfnTemplateRuleDefinition(
                Assertions=[
                    CfnTemplateRuleAssertDefinition(
                        Assert={
                            "assert1": "value1"
                        },
                        AssertDescription="assert1-description"
                    )
                ]
            )
        },
        Conditions={
            "cond1": {
                "key1": "value1"
            }
        },
        Resources={
            "resource1": CfnTemplateResourceDefinition(
                Metadata=CfnTemplateResourceMetadataDefinition(
                    CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                        Description="resource1-description",
                        Properties={
                            "BlockDeviceMappings": [
                                {
                                    "Ebs": {
                                        "Encrypted": "encrypted-description"
                                    }
                                }
                            ]
                        },
                    )
                ),
                Type="AWS::EC2::Instance",
                Properties={
                    "BlockDeviceMappings": [
                        {
                            "Ebs": {
                                "Encrypted": True
                            }
                        }
                    ],
                    "ImageId": {"Ref": "param1"}
                }
            )
        },
        Outputs={
            "out1": CfnTemplateOutputDefinition(
                Value={"Ref": "resource1"}
            )
        }
    )

    tree = CfnTemplateTree(
        template_source=CfnTemplateSource("/tmp/sample-template.yaml", context=context),
        definition=definition,
        spec_repository=spec_repository,
        context=context,
    )
    
    assert tree.description == "template-description"
    assert tree.cfn_docgen_description == "cfn-docgen-template-description"


    param1_leaf = tree.parameters_node.group_nodes["group1"].leaves["param1"]
    assert param1_leaf.definition.Type == "String"
    param2_leaf = tree.parameters_node.group_nodes[CfnTemplateParametersNode.group_name_for_independent_parameters].leaves["param2"]
    assert param2_leaf.definition.Type == "Number"

    map1_leaf = tree.mappings_node.mapping_leaves["map1"]
    assert map1_leaf.description == "map1-description"

    rule1_leaf = tree.rules_node.rule_leaves["rule1"]
    assert rule1_leaf.description == "rule1-description"

    cond1_leaf = tree.conditions_node.condition_leaves["cond1"]
    assert cond1_leaf.descirption == "cond1-description"

    resource1_node = tree.resources_node.group_nodes[tree.resources_node.group_name_for_independent_resources].resource_nodes["resource1"]
    assert resource1_node.description == "resource1-description"
    image_id_leaf = resource1_node.properties_node.property_leaves["ImageId"]
    assert image_id_leaf.description is None
    assert image_id_leaf.definition is not None and cast(Mapping[str, str], image_id_leaf.definition)["Ref"] == "param1"
    bdm_node = resource1_node.properties_node.property_nodes_list["BlockDeviceMappings"][0]
    ebs_node = bdm_node.property_nodes["Ebs"]
    encrypted_leaf = ebs_node.property_leaves["Encrypted"]
    assert encrypted_leaf.definition == True
    assert encrypted_leaf.description is not None and encrypted_leaf.description == "encrypted-description"

    out1_leaf = tree.outputs_node.output_leaves["out1"]
    assert out1_leaf.definition.Value["Ref"] == "resource1"

@pytest.mark.parametrize("filepath", [
    ("../template.yaml"), ("/tmp/template.yaml"), ("template.yaml")
])
def test_CfnTemplateSource_localfilepath_basename(
    filepath:str,
    context:AppContext,
):
    source = CfnTemplateSource(filepath, context=context)
    assert source.basename == "template.yaml"
    

def test_CfnTemplateDefinition_get_resource_groups():
    definition = CfnTemplateDefinition(
        Resources={
            "vpc-resource1" : CfnTemplateResourceDefinition(
                Type="AWS::EC2::VPC",
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/vpc/resource"
                }), # type: ignore
                Properties={}
            ),
            "vpc-resource2" : CfnTemplateResourceDefinition(
                Type="AWS::EC2::Subnet",
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/vpc/privatesubnet/subnet"
                }), # type: ignore
                Properties={}
            ),
            "not-vpc-resource": CfnTemplateResourceDefinition(
                Type="AWS::EC2::Instance",
                Metadata=None,
                Properties={}
            )
        }
    )

    resource_group = definition.get_resource_groups()
    assert len(resource_group.keys()) == 1
    assert set(resource_group["vpc"]) == set(["vpc-resource1", "vpc-resource2"])

def test_CfnTemplateResourcesNode_resource_groups(
    spec_repository:CfnSpecificationRepository,
    context:AppContext,
):
    template_definition = CfnTemplateDefinition(
        Resources={
            "vpc-resource1" : CfnTemplateResourceDefinition(
                Type="AWS::EC2::VPC",
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/Vpc/resource"
                }), # type: ignore
                Properties={}
            ),
            "vpc-resource2" : CfnTemplateResourceDefinition(
                Type="AWS::EC2::Subnet",
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/Vpc/privatesubnet/subnet"
                }), # type: ignore
                Properties={}
            ),
            "instance-resource1": CfnTemplateResourceDefinition(
                Type="AWS::EC2::Instance",
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/Instance/instance1"
                }), # type: ignore
                Properties={}
            ),
            "instance-resource2": CfnTemplateResourceDefinition(
                Type="AWS::EC2::Instance",
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/Instance/instance2"
                }), # type: ignore
                Properties={}
            ),
            "independent-resource1": CfnTemplateResourceDefinition(
                Type="AWS::EC2::Instance",
                Properties={}
            ),
            "independent-resource2": CfnTemplateResourceDefinition(
                Type="AWS::EC2::Instance",
                Properties={}
            ),
        }
    )
    resources_node = CfnTemplateResourcesNode(
        definitions=template_definition.Resources,
        spec_repository=spec_repository,
        context=context,
        resource_groups=template_definition.get_resource_groups()
    )

    vpc_node = resources_node.group_nodes["Vpc"]
    assert set(vpc_node.resource_nodes.keys()) == set(["vpc-resource1", "vpc-resource2"])
    instance_node = resources_node.group_nodes["Instance"]
    assert set(instance_node.resource_nodes.keys()) == set(["instance-resource1", "instance-resource2"])
    independent_node = resources_node.group_nodes[resources_node.group_name_for_independent_resources]
    assert set(independent_node.resource_nodes.keys()) == set(["independent-resource1", "independent-resource2"])


def test_CfnTemplateResourcesNode_as_skelton(
    spec_repository:CfnSpecificationRepository,
    context:AppContext,
):
    resource_type = CfnSpecificationResourceTypeName(
        resource_type="AWS::IAM::Role", context=context,
    )
    specs = spec_repository.get_specs_for_resource(resource_type)
    resource_node = CfnTemplateResourceNode(
        definition=CfnTemplateResourceDefinition(
            Type=resource_type.fullname,
            Properties={},
        ),
        resource_info=ResourceInfo(
            type=resource_type.fullname,
            is_recursive=spec_repository.is_recursive(resource_type),
        ),
        specs=specs,
        context=context,
    )

    skelton = resource_node.as_skelton()

    definition = CfnTemplateResourceDefinition(**skelton)

    assert definition.Type == resource_type.fullname
    assert definition.Metadata is not None and definition.Metadata.CfnDocgen is not None
    assert definition.Metadata.CfnDocgen.Description == ""
    assert definition.Metadata.CfnDocgen.Properties == {}

    p = definition.Properties
    assert p["AssumeRolePolicyDocument"] == "Json"
    assert p["Description"] == "String"
    assert p["ManagedPolicyArns"] == "List of String"
    assert p["MaxSessionDuration"] == "Integer"
    assert p["Path"] == "String"
    assert p["PermissionsBoundary"] == "String"
    policies = cast(List[Mapping[str, str]], p["Policies"])
    assert len(policies) == 1
    assert policies[0]["PolicyDocument"] == "Json"
    assert policies[0]["PolicyName"] == "String"
    assert p["RoleName"] == "String"
    tags = cast(List[Mapping[str, str]], p["Tags"])
    assert len(tags) == 1
    assert tags[0]["Key"] == "String"
    assert tags[0]["Value"] == "String"

