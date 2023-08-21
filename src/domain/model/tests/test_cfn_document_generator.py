
from typing import Any, List, Optional, Union
import pytest
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig
from domain.model.cfn_document_generator import CfnMarkdownDocumentGenerator, PropertyField

from domain.model.cfn_template import CfnTemplateConditionsNode, CfnTemplateDefinition, CfnTemplateMappingsNode, CfnTemplateMetadataCfnDocgenDefinition, CfnTemplateMetadataDefinition, CfnTemplateMetadataInterface, CfnTemplateMetadataParameterGroup, CfnTemplateMetadataParameterGroupLabel, CfnTemplateOutputDefinition, CfnTemplateOutputExportDefinition, CfnTemplateOutputsNode, CfnTemplateParameterDefinition, CfnTemplateParametersNode, CfnTemplateResourceDefinition, CfnTemplateResourceMetadataCfnDocgenDefinition, CfnTemplateResourceMetadataDefinition, CfnTemplateResourcesNode, CfnTemplateRuleAssertDefinition, CfnTemplateRuleDefinition, CfnTemplateRulesNode, CfnTemplateSource, CfnTemplateTree


@pytest.fixture
def cfn_template_tree():
    spec_repository = CfnSpecificationRepository(
        source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
        loader=RemoteFileLoader(),
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
    )

    definition = CfnTemplateDefinition(
        AWSTemplateFormatVersion="2012-10",
        Description="template-description",
        Metadata=CfnTemplateMetadataDefinition(**{
            'AWS::CloudFormation::Interface': CfnTemplateMetadataInterface(
                ParameterGroups=[
                    CfnTemplateMetadataParameterGroup(
                        Label=CfnTemplateMetadataParameterGroupLabel(
                            default="Group1"
                        ),
                        Parameters=["Param1"]
                    )
                ]
            ),
            "CfnDocgen": CfnTemplateMetadataCfnDocgenDefinition(
                Description="- line1\n- line2",
                Mappings={
                    "Map1": "map1-description"
                },
                Rules={
                    "Rule1": "rule1-description"
                },
                Conditions={
                    "Cond1": "cond1-description"
                },
            )
        }), # type: ignore
        Parameters={
            "Param1": CfnTemplateParameterDefinition(
                Type="String"
            ),
            "Param2": CfnTemplateParameterDefinition(
                Type="Number"
            )
        },
        Mappings={
            "Map1": {
                "name1": {
                    "key1": "value1"
                }
            }
        },
        Rules={
            "Rule1": CfnTemplateRuleDefinition(
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
            "Cond1": {
                "key1": "value1"
            }
        },
        Resources={
            "Resource1": CfnTemplateResourceDefinition(
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
            ),
            "Resource2": CfnTemplateResourceDefinition(
                Type="AWS::CertificateManager::Certificate",
                Properties={}
            )
        },
        Outputs={
            "Out1": CfnTemplateOutputDefinition(
                Value={"Ref": "resource1"}
            )
        }
    )

    return CfnTemplateTree(
        template_source=CfnTemplateSource("/tmp/template.yaml"),
        definition=definition,
        spec_repository=spec_repository,
    )

@pytest.mark.parametrize("original,expected", [
    ("template.yaml", "templateyaml"),
    ("Map_1", "map_1"),
    ("Resource (AWS::EC2::Instance)", "resource-awsec2instance"),
])
def test_MarkdownDocumentGenerator_toc_escape(original:str, expected:str):
    generator = CfnMarkdownDocumentGenerator()
    escape = generator._toc_escape(original) # type: ignore
    assert escape == expected 


def test_MarkdownDocumentGenerator_table_of_contents(cfn_template_tree:CfnTemplateTree):

    generator = CfnMarkdownDocumentGenerator()
    expected_toc = "\n".join([
        "- [template.yaml](#templateyaml)",
        "  - [Description](#description)",
        "  - [Parameters](#parameters)",
        "    - [Group1](#group1)",
        "      - [Param1](#param1)",
        "      - [Param2](#param2)",
        "  - [Mappings](#mappings)",
        "    - [Map1](#map1)",
        "  - [Conditions](#conditions)",
        "    - [Cond1](#cond1)",
        "  - [Rules](#rules)",
        "    - [Rule1](#rule1)",
        "  - [Resources](#resources)",
        "    - [Resource2 (AWS::CertificateManager::Certificate)](#resource2-awscertificatemanagercertificate)",
        "    - [Resource1 (AWS::EC2::Instance)](#resource1-awsec2instance)",
        "  - [Outputs](#outputs)",
        "    - [Out1](#out1)"
    ])
    toc = generator.table_of_contents(cfn_template_tree)
    assert toc == expected_toc


@pytest.mark.parametrize("version,description,transform,e_version,e_description,e_transform", [
    ("2012-10", "template-descirption", "t1", "2012-10", "template-descirption", "t1"),
    ("2012-10", "template-descirption", ["t1", "t2"], "2012-10", "template-descirption", "<ul><li>t1</li><li>t2</li></ul>"),
    (None, None, [], "-", "-", "-"),
])
def test_MarkdownDocumentGenerator_overview(
    version:Optional[str], description:Optional[str], transform:Union[str, List[str]],
    e_version:str, e_description:str, e_transform:str,
    cfn_template_tree:CfnTemplateTree,
):
    generator = CfnMarkdownDocumentGenerator()
    expected_overview = "\n".join([
        "# template.yaml",
        "",
        "| | |",
        "|-|-|",
        f"|AWSTemplateFormatVersion|{e_version}|",
        f"|Description|{e_description}|",
        f"|Transform|{e_transform}|",
    ])
    cfn_template_tree.aws_template_format_version = version
    cfn_template_tree.description = description
    cfn_template_tree.transform = transform
    overview = generator.overview(cfn_template_tree)
    assert overview == expected_overview

@pytest.mark.parametrize("cfn_docgen_description,e_cfn_docgen_description",[
    (
        "cfn-docgen-description",
        "\n".join([
            "## Description",
            "",
            "cfn-docgen-description",
        ]),
    ),
    (
        None,
        "\n".join([
            "## Description",
            "",
        ]),
    ),
    (
        "- d1\n- d2",
        "\n".join([
            "## Description",
            "",
            "- d1\n- d2",
        ]),
    )
])
def test_MarkdownDocumentGenerator_description(
        cfn_docgen_description:Optional[str], e_cfn_docgen_description:str,
        cfn_template_tree:CfnTemplateTree,
):
    generator = CfnMarkdownDocumentGenerator()
    cfn_template_tree.cfn_docgen_description = cfn_docgen_description
    description = generator.description(cfn_template_tree)
    assert description == e_cfn_docgen_description

@pytest.mark.parametrize("paramters_node,e_parameters",[
    (
        # without parameter groups
        CfnTemplateParametersNode(
            definitions={
                "param1": CfnTemplateParameterDefinition(
                    AllowedPattern="allowedpattern",
                    AllowedValues=["s1", "s2"],
                    ConstraintDescription="constraintdescription",
                    Default="s1",
                    Description="param1-description",
                    MaxLength=10,
                    MinLength=2,
                    MaxValue=None,
                    MinValue=None,
                    NoEcho=True,
                    Type="String",
                ),
                "param2": CfnTemplateParameterDefinition(Type="Number"),
            },
            parameter_groups=[]
        ),
        "\n".join([
            "## Parameters",
            "",
            "#### param1",
            "",
            "param1-description",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|String|s1|<ul><li>s1</li><li>s2</li></ul>|allowedpattern|true|-|-|2|10|constraintdescription|",
            "",
            "#### param2",
            "",
            "",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|Number|-|-|-|false|-|-|-|-|-|",
        ])
    ),
    (
        # with parameter groups
        CfnTemplateParametersNode(
            definitions={
                "param1": CfnTemplateParameterDefinition(
                    AllowedPattern="allowedpattern",
                    AllowedValues=["s1", "s2"],
                    ConstraintDescription="constraintdescription",
                    Default="s1",
                    Description="param1-description",
                    MaxLength=10,
                    MinLength=2,
                    MaxValue=None,
                    MinValue=None,
                    NoEcho=True,
                    Type="String",
                ),
                "param2": CfnTemplateParameterDefinition(Type="Number"),
            },
            parameter_groups=[
                CfnTemplateMetadataParameterGroup(
                    Label=CfnTemplateMetadataParameterGroupLabel(default="Group1"),
                    Parameters=["param1", "param2"]
                )
            ]
        ),
        "\n".join([
            "## Parameters",
            "",
            "### Group1",
            "",
            "#### param1",
            "",
            "param1-description",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|String|s1|<ul><li>s1</li><li>s2</li></ul>|allowedpattern|true|-|-|2|10|constraintdescription|",
            "",
            "#### param2",
            "",
            "",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|Number|-|-|-|false|-|-|-|-|-|",
        ])
    ),
    (
        # partially with parameter groups
        CfnTemplateParametersNode(
            definitions={
                "param1": CfnTemplateParameterDefinition(
                    AllowedPattern="allowedpattern",
                    AllowedValues=["s1", "s2"],
                    ConstraintDescription="constraintdescription",
                    Default="s1",
                    Description="param1-description",
                    MaxLength=10,
                    MinLength=2,
                    MaxValue=None,
                    MinValue=None,
                    NoEcho=True,
                    Type="String",
                ),
                "param2": CfnTemplateParameterDefinition(Type="Number"),
            },
            parameter_groups=[
                CfnTemplateMetadataParameterGroup(
                    Label=CfnTemplateMetadataParameterGroupLabel(default="Group1"),
                    Parameters=["param2"]
                )
            ]
        ),
        "\n".join([
            "## Parameters",
            "",
            "### Group1",
            "",
            "#### param2",
            "",
            "",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|Number|-|-|-|false|-|-|-|-|-|",
            "",
            "#### param1",
            "",
            "param1-description",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|String|s1|<ul><li>s1</li><li>s2</li></ul>|allowedpattern|true|-|-|2|10|constraintdescription|",
        ])
    ),
    (
        # no parameters
        CfnTemplateParametersNode(
            definitions={},
            parameter_groups=[]
        ),
        "\n".join([
            "## Parameters",
        ])
    )
])
def test_MarkdownDocumentGenerator_parameters(
        paramters_node:CfnTemplateParametersNode, e_parameters:str,
        cfn_template_tree:CfnTemplateTree,
):
    generator = CfnMarkdownDocumentGenerator()
    cfn_template_tree.parameters_node = paramters_node

    parameters = generator.parameters(cfn_template_tree)
    assert parameters == e_parameters

@pytest.mark.parametrize("mappings_node,e_mappings", [
    (
        CfnTemplateMappingsNode(
            definitions={
                "map1": {
                    "name1": {
                        "key11": "value11",
                        "key12": "value12",
                    }
                },
                "map2": {
                    "name2": {
                        "key2": "value2"
                    }
                }
            },
            descriptions={
                "map1": "map1-description"
            }
        ),
        "\n".join([
            "## Mappings",
            "",
            "### map1",
            "",
            "map1-description",
            "",
            "|Map|Key|Value|",
            "|-|-|-|",
            "|name1|key11|value11|",
            "|name1|key12|value12|",
            "",
            "### map2",
            "",
            "",
            "",
            "|Map|Key|Value|",
            "|-|-|-|",
            "|name2|key2|value2|",
        ])
    ),
    (
        CfnTemplateMappingsNode(
            definitions={},
            descriptions={}
        ),
        "\n".join([
            "## Mappings",
        ])
    )
])
def test_MarkdownDocumentGenerator_mappings(
        mappings_node:CfnTemplateMappingsNode, e_mappings:str,
        cfn_template_tree:CfnTemplateTree,
):
    generator = CfnMarkdownDocumentGenerator()
    cfn_template_tree.mappings_node = mappings_node
    
    mappings = generator.mappings(cfn_template_tree)
    assert mappings == e_mappings


@pytest.mark.parametrize("conditions_node,e_conditions", [
    (
        CfnTemplateConditionsNode(
            definitions={
                "cond1": {
                    "Fn::Equals": [
                        {"Ref": "AWS::Region"},
                        "ap-northeast-1"
                    ]
                },
                "cond2": {
                    "Fn::Equals": [1, 1]
                }
            },
            descriptions={
                "cond1": "cond1-description"
            }
        ),
        "\n".join([
            "## Conditions",
            "",
            "### cond1",
            "",
            "cond1-description",
            "",
            "|Condition|",
            "|-|",
            '|{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;]<br/>}|',
            "",
            "### cond2",
            "",
            "",
            "",
            "|Condition|",
            "|-|",
            '|{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;1,<br/>&nbsp;&nbsp;&nbsp;&nbsp;1<br/>&nbsp;&nbsp;]<br/>}|',
        ])
    ),
    (
        CfnTemplateConditionsNode(
            definitions={},
            descriptions={}
        ),
        "\n".join([
            "## Conditions",
        ])
    )
])
def test_MarkdownDocumentGenerator_conditions(
        conditions_node:CfnTemplateConditionsNode, e_conditions:str,
        cfn_template_tree:CfnTemplateTree,
):
    generator = CfnMarkdownDocumentGenerator()
    cfn_template_tree.conditions_node = conditions_node
    
    conditions = generator.conditions(cfn_template_tree)
    assert conditions == e_conditions

@pytest.mark.parametrize("j,expected", [
    (
        {
            "Fn::Equals": [
                {
                    "Ref": "AWS::Region"
                },
                "ap-northeast-1"
            ]
        },
        '{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;]<br/>}',
    ),
    (
        [
            {
                "Ref": "AWS::NoValue"
            },
            {
                "Ref": "AWS::Region"
            }
        ],
        '[<br/>&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::NoValue"<br/>&nbsp;&nbsp;},<br/>&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;}<br/>]',
    ),
    (
        "string",
        "string"
    ),
    (
        True,
        "true"
    )
])
def test_MarkdownDocumentGenerator_dump_json(j:Any,expected:str):
    generator = CfnMarkdownDocumentGenerator()

    dumped = generator._dump_json(j) # type: ignore
    print(dumped)
    assert dumped == expected
    

@pytest.mark.parametrize("rules_node,e_rules",[
    (
        CfnTemplateRulesNode(
            definitions={
                "rule1": CfnTemplateRuleDefinition(
                    RuleCondition={
                        "Fn::Equals": [
                            {
                                "Ref": "AWS::Region"
                            },
                            "ap-northeast-1"
                        ]
                    },
                    Assertions=[
                        CfnTemplateRuleAssertDefinition(
                            Assert={
                                "Fn::Equals": [
                                    {
                                        "Ref": "AWS::Region"
                                    },
                                    "ap-northeast-1"
                                ]
                            },
                            AssertDescription="assert-description1"
                        ),
                        CfnTemplateRuleAssertDefinition(
                            Assert={
                                "Fn::Equals": [
                                    {
                                        "Ref": "AWS::Region"
                                    },
                                    "ap-northeast-1"
                                ]
                            },
                            AssertDescription="assert-description2"
                        )
                    ]
                ),
                "rule2": CfnTemplateRuleDefinition(
                    RuleCondition=None,
                    Assertions=[
                        CfnTemplateRuleAssertDefinition(
                            Assert={"str":"str"},
                            AssertDescription="assert-description2"
                        )
                    ]
                )
            },
            descriptions={
                "rule1": "rule1-description"
            }
        ),
        "\n".join([
            "## Rules",
            "",
            "### rule1",
            "",
            "rule1-description",
            "",
            "|RuleCondition|",
            "|-|",
            '|{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;]<br/>}|',
            "",
            "|Assert|AssertDescription|",
            "|-|-|",
            '|{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;]<br/>}|assert-description1|',
            '|{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;]<br/>}|assert-description2|',
            "",
            "### rule2",
            "",
            "",
            "",
            "|RuleCondition|",
            "|-|",
            "|-|",
            "",
            "|Assert|AssertDescription|",
            "|-|-|",
            '|{<br/>&nbsp;&nbsp;"str":&nbsp;"str"<br/>}|assert-description2|',
        ])
    ),
    (
        CfnTemplateRulesNode(
            definitions={},
            descriptions={},
        ),
        "\n".join([
            "## Rules",
        ])
    )
])
def test_MarkdownDocumentGenerator_rules(
    rules_node:CfnTemplateRulesNode, e_rules:str, 
    cfn_template_tree:CfnTemplateTree
):
    generator = CfnMarkdownDocumentGenerator()
    cfn_template_tree.rules_node = rules_node

    rules = generator.rules(cfn_template_tree)
    assert rules == e_rules


@pytest.mark.parametrize("resources_node,e_resources", [
    (
        CfnTemplateResourcesNode(
            definitions={
                "Instance": CfnTemplateResourceDefinition(
                    Type="AWS::EC2::Instance",
                    DependsOn=[
                        "Vpc", "Subnet",
                    ],
                    Condition="Cond",
                    CreationPolicy={"Creation": "Policy"},
                    UpdatePolicy={"Update": "Policy"},
                    UpdateReplacePolicy="Snapshot",
                    DeletionPolicy="Retain",
                    Metadata=CfnTemplateResourceMetadataDefinition(
                        CfnDocgen=CfnTemplateResourceMetadataCfnDocgenDefinition(
                            Description="instance-description",
                            Properties={
                                "ImageId": "imageid",
                                "CpuOptions": "cpuoptions",
                                "BlockDeviceMappings": [
                                    {
                                        "Ebs": {
                                            "Encrypted": "encrypted"
                                        }
                                    }
                                ]
                            }
                        )
                    ),
                    Properties={
                        "ImageId": "IMAGEID",
                        "CpuOptions": {
                            "CoreCount": 0,
                        },
                        "BlockDeviceMappings": [
                            {
                                "Ebs": {
                                    "Encrypted": True,
                                    "VolumeType": "VOLUMETYPE",
                                }
                            },
                            {
                                "NoDevice": {}
                            }
                        ],
                        "SecurityGroupIds": [
                            "SECURITYGROUPID1",
                            "SECURITYGROUPID2",
                        ],
                        "SsmAssociations": [
                            {
                                "AssociationParameters": [
                                    {
                                        "Key": "KEY1",
                                        "Value": ["VALUE11", "VALUE12"]
                                    },
                                    {
                                        "Key": "KEY2",
                                        "Value": ["VALUE21", "VALUE22"]
                                    }
                                ]
                            }
                        ]
                    }
                ),
                "Table": CfnTemplateResourceDefinition(
                    Type="AWS::DynamoDB::Table",
                    Metadata=None,
                    Properties={
                        "TableName": "TABLENAME"
                    },
                )
            },
            spec_repository=CfnSpecificationRepository(
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                loader=RemoteFileLoader(),
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            )
        ),
        "\n".join([
            "## Resources",
            "",
            "### [Table (AWS::DynamoDB::Table)](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)",
            "",
            "",
            "",
            "|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|",
            "|-|-|-|-|-|-|",
            "|-|-|-|-|Delete|Delete|",
            "",
            "|Property|Value|Description|Type|Required|UpdateType|",
            "|-|-|-|-|-|-|",
            "|TableName|TABLENAME|-|String|false|Immutable|",
            "",
            "### [Instance (AWS::EC2::Instance)](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html)",
            "",
            "instance-description",
            "",
            "|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|",
            "|-|-|-|-|-|-|",
            '|[<br/>&nbsp;&nbsp;"Vpc",<br/>&nbsp;&nbsp;"Subnet"<br/>]|Cond|{<br/>&nbsp;&nbsp;"Creation":&nbsp;"Policy"<br/>}|{<br/>&nbsp;&nbsp;"Update":&nbsp;"Policy"<br/>}|Snapshot|Retain|',
            "",
            "|Property|Value|Description|Type|Required|UpdateType|",
            "|-|-|-|-|-|-|",
            "|BlockDeviceMappings[0]|-|-|List of BlockDeviceMapping|false|Conditional|",
            "|&nbsp;&nbsp;Ebs|-|-|Ebs|false|Mutable|",
            "|&nbsp;&nbsp;&nbsp;&nbsp;Encrypted|true|encrypted|Boolean|false|Mutable|",
            "|&nbsp;&nbsp;&nbsp;&nbsp;VolumeType|VOLUMETYPE|-|String|false|Mutable|",
            "|BlockDeviceMappings[1]|-|-|List of BlockDeviceMapping|false|Conditional|",
            "|&nbsp;&nbsp;NoDevice|-|-|NoDevice|false|Mutable|",
            "|CpuOptions|-|cpuoptions|CpuOptions|false|Immutable|",
            "|&nbsp;&nbsp;CoreCount|0|-|Integer|false|Mutable|",
            "|ImageId|IMAGEID|imageid|String|false|Immutable|",
            '|SecurityGroupIds|[<br/>&nbsp;&nbsp;"SECURITYGROUPID1",<br/>&nbsp;&nbsp;"SECURITYGROUPID2"<br/>]|-|List of String|false|Conditional|',
            '|SsmAssociations[0]|-|-|List of SsmAssociation|false|Mutable|',
            '|&nbsp;&nbsp;AssociationParameters[0]|-|-|List of AssociationParameter|false|Mutable|',
            '|&nbsp;&nbsp;&nbsp;&nbsp;Key|KEY1|-|String|true|Mutable|',
            '|&nbsp;&nbsp;&nbsp;&nbsp;Value|[<br/>&nbsp;&nbsp;"VALUE11",<br/>&nbsp;&nbsp;"VALUE12"<br/>]|-|List of String|true|Mutable|',
            '|&nbsp;&nbsp;AssociationParameters[1]|-|-|List of AssociationParameter|false|Mutable|',
            '|&nbsp;&nbsp;&nbsp;&nbsp;Key|KEY2|-|String|true|Mutable|',
            '|&nbsp;&nbsp;&nbsp;&nbsp;Value|[<br/>&nbsp;&nbsp;"VALUE21",<br/>&nbsp;&nbsp;"VALUE22"<br/>]|-|List of String|true|Mutable|',
        ])
    ),
    (
        CfnTemplateResourcesNode(
            definitions={},
            spec_repository=CfnSpecificationRepository(
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                loader=RemoteFileLoader(),
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            )
        ),
        "\n".join([
            "## Resources",
        ])
    )
])
def test_MarkdownDocumentGenerator_resources(
        resources_node:CfnTemplateResourcesNode, e_resources:str,
        cfn_template_tree:CfnTemplateTree,
):
    generator = CfnMarkdownDocumentGenerator()
    cfn_template_tree.resources_node = resources_node

    resources = generator.resources(cfn_template_tree)
    assert resources == e_resources

def test_MarkdownDocumentGenerator_flatten_properties():
    cfn_template_tree = CfnTemplateResourcesNode(
        definitions={
            "Instance": CfnTemplateResourceDefinition(
                Type="AWS::EC2::Instance",
                DependsOn=[
                    "Vpc", "Subnet",
                ],
                Condition="Cond",
                CreationPolicy={"Creation": "Policy"},
                UpdatePolicy={"Update": "Policy"},
                UpdateReplacePolicy="Snapshot",
                DeletionPolicy="Retain",
                Properties={
                    "ImageId": "IMAGEID",
                    "CpuOptions": {
                        "CoreCount": 0,
                    },
                    "BlockDeviceMappings": [
                        {
                            "Ebs": {
                                "Encrypted": True,
                                "VolumeType": "VOLUMETYPE",
                            }
                        },
                        {
                            "NoDevice": {}
                        }
                    ],
                    "SecurityGroupIds": [
                        "SECURITYGROUPID1",
                        "SECURITYGROUPID2",
                    ],
                    "SsmAssociations": [
                        {
                            "AssociationParameters": [
                                {
                                    "Key": "KEY1",
                                    "Value": ["VALUE11", "VALUE12"]
                                },
                                {
                                    "Key": "KEY2",
                                    "Value": ["VALUE21", "VALUE22"]
                                }
                            ]
                        }
                    ]
                }
            )
        },
        spec_repository=CfnSpecificationRepository(
            source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
            loader=RemoteFileLoader(),
            cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
            recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        )
    )
    expected:List[PropertyField] = [
        PropertyField(
            Property="BlockDeviceMappings[0]", Type="List of BlockDeviceMapping",
            Value="-", Description="-", Required="false", UpdateType="Conditional",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;Ebs", Type="Ebs",
            Value="-", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;&nbsp;&nbsp;Encrypted", Type="Boolean",
            Value="true", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;&nbsp;&nbsp;VolumeType", Type="String",
            Value="VOLUMETYPE", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="BlockDeviceMappings[1]", Type="List of BlockDeviceMapping",
            Value="-", Description="-", Required="false", UpdateType="Conditional",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;NoDevice", Type="NoDevice",
            Value="-", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="CpuOptions", Type="CpuOptions",
            Value="-", Description="-", Required="false", UpdateType="Immutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;CoreCount", Type="Integer",
            Value="0", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="ImageId", Type="String",
            Value="IMAGEID", Description="-", Required="false", UpdateType="Immutable",
        ),
        PropertyField(
            Property="SecurityGroupIds", Type="List of String",
            Value='[<br/>&nbsp;&nbsp;"SECURITYGROUPID1",<br/>&nbsp;&nbsp;"SECURITYGROUPID2"<br/>]', Description="-", Required="false", UpdateType="Conditional",
        ),
        PropertyField(
            Property="SsmAssociations[0]", Type="List of SsmAssociation",
            Value="-", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;AssociationParameters[0]", Type="List of AssociationParameter",
            Value="-", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;&nbsp;&nbsp;Key", Type="String",
            Value="KEY1", Description="-", Required="true", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;&nbsp;&nbsp;Value", Type="List of String",
            Value='[<br/>&nbsp;&nbsp;"VALUE11",<br/>&nbsp;&nbsp;"VALUE12"<br/>]', Description="-", Required="true", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;AssociationParameters[1]", Type="List of AssociationParameter",
            Value="-", Description="-", Required="false", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;&nbsp;&nbsp;Key", Type="String",
            Value="KEY2", Description="-", Required="true", UpdateType="Mutable",
        ),
        PropertyField(
            Property="&nbsp;&nbsp;&nbsp;&nbsp;Value", Type="List of String",
            Value='[<br/>&nbsp;&nbsp;"VALUE21",<br/>&nbsp;&nbsp;"VALUE22"<br/>]', Description="-", Required="true", UpdateType="Mutable",
        ),
    ]

    generator = CfnMarkdownDocumentGenerator()

    properties = generator._flatten_properties_node(cfn_template_tree.resource_nodes["Instance"].properties_node) # type: ignore
    assert len(properties) == len(expected)
    for p, e in zip(properties, expected):
        print(p)
        assert p.Property == e.Property
        assert p.Type == e.Type
        assert p.Value == e.Value
        assert p.Description == e.Description
        assert p.Required == e.Required
        assert p.UpdateType == e.UpdateType, p


@pytest.mark.parametrize("jsonpath,expected", [
    ("$.BlockDeviceMappings", "BlockDeviceMappings"),
    ("$.BlockDeviceMappings[0]", "BlockDeviceMappings[0]"),
    ("$.BlockDeviceMappings[0].Ebs", "&nbsp;&nbsp;Ebs"),
    ("$.BlockDeviceMappings[0].Ebs.Encrypted", "&nbsp;&nbsp;&nbsp;&nbsp;Encrypted"),
    ("$.SsmAssociations[0].AssociationParameters[0]", "&nbsp;&nbsp;AssociationParameters[0]"),
    ("$.SsmAssociations[0].AssociationParameters[0].Key", "&nbsp;&nbsp;&nbsp;&nbsp;Key"),
])
def test_MarkdownDocumentGenerator_simplify_jsonpath(jsonpath:str, expected:str):
    generator = CfnMarkdownDocumentGenerator()
    path = generator._simplify_jsonpath(jsonpath) # type: ignore
    assert path == expected


@pytest.mark.parametrize("outputs_node,e_outputs", [
    (
        CfnTemplateOutputsNode(
            definitions={
                "out1": CfnTemplateOutputDefinition(
                    Description="out1-description",
                    Value={"Ref": "VALUE"},
                    Export=CfnTemplateOutputExportDefinition(
                        Name={"Ref": "NAME"}
                    ),
                    Condition="cond1"
                ),
                "out2": CfnTemplateOutputDefinition(
                    Value="VALUE"
                )
            }
        ),
        "\n".join([
            "## Outputs",
            "",
            "### out1",
            "",
            "out1-description",
            "",
            "|Value|ExportName|Condition|",
            "|-|-|-|",
            '|{<br/>&nbsp;&nbsp;"Ref":&nbsp;"VALUE"<br/>}|{<br/>&nbsp;&nbsp;"Ref":&nbsp;"NAME"<br/>}|cond1|',
            "",
            "### out2",
            "",
            "",
            "",
            "|Value|ExportName|Condition|",
            "|-|-|-|",
            "|VALUE|-|-|",
        ])
    ),
    (
        CfnTemplateOutputsNode(
            definitions={}
        ),
        "\n".join([
            "## Outputs",
        ])
    )
])
def test_MarkdownDocumentGenerator_outputs(
    outputs_node:CfnTemplateOutputsNode, e_outputs:str,
    cfn_template_tree:CfnTemplateTree,
):
    cfn_template_tree.outputs_node = outputs_node
    generator = CfnMarkdownDocumentGenerator()
    outputs = generator.outputs(cfn_template_tree)
    print(outputs)
    assert outputs == e_outputs

@pytest.mark.parametrize("tree,e_template", [
    (
        CfnTemplateTree(
            template_source=CfnTemplateSource("template.yaml"),
            definition=CfnTemplateDefinition(
                Resources={"resource1": CfnTemplateResourceDefinition(
                    Type="AWS::EC2::Instance",
                    Properties={},
                )}
            ),
            spec_repository=CfnSpecificationRepository(
                loader=RemoteFileLoader(),
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            )
        ),
        "\n".join([
            "- [template.yaml](#templateyaml)",
            "  - [Description](#description)",
            "  - [Parameters](#parameters)",
            "  - [Mappings](#mappings)",
            "  - [Conditions](#conditions)",
            "  - [Rules](#rules)",
            "  - [Resources](#resources)",
            "    - [resource1 (AWS::EC2::Instance)](#resource1-awsec2instance)",
            "  - [Outputs](#outputs)",
            "",
            "---",
            "",
            "# template.yaml",
            "",
            "| | |",
            "|-|-|",
            "|AWSTemplateFormatVersion|-|",
            "|Description|-|",
            "|Transform|-|",
            "",
            "---",
            "",
            "## Description",
            "",
            "",
            "---",
            "",
            "## Parameters",
            "",
            "---",
            "",
            "## Mappings",
            "",
            "---",
            "",
            "## Conditions",
            "",
            "---",
            "",
            "## Rules",
            "",
            "---",
            "",
            "## Resources",
            "",
            "### [resource1 (AWS::EC2::Instance)](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html)",
            "",
            "",
            "",
            "|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|",
            "|-|-|-|-|-|-|",
            "|-|-|-|-|Delete|Delete|",
            "",
            "|Property|Value|Description|Type|Required|UpdateType|",
            "|-|-|-|-|-|-|",
            "",
            "---",
            "",
            "## Outputs",
        ])
    )
])
def test_MarkdownDocumentGenerator_generate(tree:CfnTemplateTree, e_template:str):
    generator = CfnMarkdownDocumentGenerator()
    template = generator.generate(tree)
    assert template == e_template
