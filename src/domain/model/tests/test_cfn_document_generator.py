
from typing import Any, List, Optional, Union
import pytest
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig
from domain.model.cfn_document_generator import MarkdownDocumentGenerator

from domain.model.cfn_template import CfnTemplateConditionsNode, CfnTemplateDefinition, CfnTemplateMappingsNode, CfnTemplateMetadataCfnDocgenDefinition, CfnTemplateMetadataDefinition, CfnTemplateMetadataInterface, CfnTemplateMetadataParameterGroup, CfnTemplateMetadataParameterGroupLabel, CfnTemplateOutputDefinition, CfnTemplateParameterDefinition, CfnTemplateParametersNode, CfnTemplateResourceDefinition, CfnTemplateResourceMetadataCfnDocgenDefinition, CfnTemplateResourceMetadataDefinition, CfnTemplateRuleAssertDefinition, CfnTemplateRuleDefinition, CfnTemplateRulesNode, CfnTemplateSource, CfnTemplateTree


@pytest.fixture
def cfn_template_tree():
    spec_repository = CfnSpecificationRepository(
        loader=RemoteFileLoader(AppConfig.DEFAULT_SPECIFICATION_URL),
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
    generator = MarkdownDocumentGenerator()
    escape = generator._toc_escape(original) # type: ignore
    assert escape == expected 


def test_MarkdownDocumentGenerator_table_of_contents(cfn_template_tree:CfnTemplateTree):

    generator = MarkdownDocumentGenerator()
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
    generator = MarkdownDocumentGenerator()
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
    ("cfn-docgen-description", "cfn-docgen-description"),
    (None, ""),
    ("- d1\n- d2", "- d1\n- d2")
])
def test_MarkdownDocumentGenerator_description(
        cfn_docgen_description:Optional[str], e_cfn_docgen_description:str,
        cfn_template_tree:CfnTemplateTree,
):
    generator = MarkdownDocumentGenerator()
    expected_description = "\n".join([
        "## Description",
        "",
        e_cfn_docgen_description,
    ])
    cfn_template_tree.cfn_docgen_description = cfn_docgen_description
    description = generator.description(cfn_template_tree)
    assert description == expected_description

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
    generator = MarkdownDocumentGenerator()
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
    generator = MarkdownDocumentGenerator()
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
            "|Conditions|",
            "|-|",
            '|{<br/>&nbsp;&nbsp;"Fn::Equals":&nbsp;[<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref":&nbsp;"AWS::Region"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;]<br/>}|',
            "",
            "### cond2",
            "",
            "",
            "",
            "|Conditions|",
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
    generator = MarkdownDocumentGenerator()
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
])
def test_MarkdownDocumentGenerator_dump_json(j:Any,expected:str):
    generator = MarkdownDocumentGenerator()

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
    generator = MarkdownDocumentGenerator()
    cfn_template_tree.rules_node = rules_node

    rules = generator.rules(cfn_template_tree)
    assert rules == e_rules



# ## Rules

# ### RegionRule

# This template is available only in ap-northeast-1

# |RuleCondition|
# |-|
# |-|

# |Assert|AssertDescription|
# |-|-|