import logging
from typing import Any, List, Optional, Union
import pytest
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import CfnMarkdownDocumentGenerator, PropertyField

from cfn_docgen.domain.model.cfn_template import CfnTemplateConditionsNode, CfnTemplateDefinition, CfnTemplateMappingsNode, CfnTemplateMetadataCfnDocgenDefinition, CfnTemplateMetadataDefinition, CfnTemplateMetadataInterface, CfnTemplateMetadataParameterGroup, CfnTemplateMetadataParameterGroupLabel, CfnTemplateOutputDefinition, CfnTemplateOutputExportDefinition, CfnTemplateOutputsNode, CfnTemplateParameterDefinition, CfnTemplateParametersNode, CfnTemplateResourceDefinition, CfnTemplateResourceMetadataCfnDocgenDefinition, CfnTemplateResourceMetadataDefinition, CfnTemplateResourcesNode, CfnTemplateRuleAssertDefinition, CfnTemplateRuleDefinition, CfnTemplateRulesNode, CfnTemplateSource, CfnTemplateTree

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

@pytest.fixture
def cfn_template_tree(context:AppContext):
    spec_repository = CfnSpecificationRepository(
        source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        context=context,
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
        template_source=CfnTemplateSource("/tmp/template.yaml", context=AppContext(log_level=logging.DEBUG)),
        definition=definition,
        spec_repository=spec_repository,
        context=context
    )

def test_CfnMarkdownDocumentGenerator_header(
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    header = generator.header()
    from cfn_docgen import __version__
    expected = f"<!-- cfn-docgen: generated by v{__version__} -->"
    assert header == expected

@pytest.mark.parametrize("original,expected", [
    ("template.yaml", "templateyaml"),
    ("Map_1", "map_1"),
    ("Resource (AWS::EC2::Instance)", "resource-awsec2instance"),
])
def test_CfnMarkdownDocumentGenerator_toc_escape(
    original:str, expected:str,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    escape = generator._toc_escape(original) # type: ignore
    assert escape == expected 


def test_CfnMarkdownDocumentGenerator_table_of_contents(
    cfn_template_tree:CfnTemplateTree,
    context:AppContext,
):

    generator = CfnMarkdownDocumentGenerator(context=context)
    expected_toc = "\n".join([
        "- [template.yaml](#templateyaml)",
        "  - [Description](#description)",
        "  - [Parameters](#parameters)",
        "    - [Group1](#group1)",
        "      - [Param1](#param1)",
        "    - [Param2](#param2)",
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


def test_CfnMarkdownDocumentGenerator_table_of_contents_with_resource_groups(
    context:AppContext,
):

    generator = CfnMarkdownDocumentGenerator(context=context)
    expected_toc = "\n".join([
        "- [template.yaml](#templateyaml)",
        "  - [Description](#description)",
        "  - [Parameters](#parameters)",
        "  - [Mappings](#mappings)",
        "  - [Conditions](#conditions)",
        "  - [Rules](#rules)",
        "  - [Resources](#resources)",
        "    - [ResourceGroup1](#resourcegroup1)",
        "      - [Resource12 (AWS::CertificateManager::Certificate)](#resource12-awscertificatemanagercertificate)",
        "      - [Resource11 (AWS::EC2::Instance)](#resource11-awsec2instance)",
        "    - [ResourceGroup2](#resourcegroup2)",
        "      - [Resource22 (AWS::CertificateManager::Certificate)](#resource22-awscertificatemanagercertificate)",
        "      - [Resource21 (AWS::EC2::Instance)](#resource21-awsec2instance)",
        "  - [Outputs](#outputs)",
    ])
    spec_repository = CfnSpecificationRepository(
        source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        context=context,
    )

    definition = CfnTemplateDefinition(
        Resources={
            "Resource11": CfnTemplateResourceDefinition(
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/ResourceGroup1/resource11"
                }), # type: ignore
                Type="AWS::EC2::Instance",
                Properties={}
            ),
            "Resource12": CfnTemplateResourceDefinition(
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/ResourceGroup1/resource12"
                }), # type: ignore
                Type="AWS::CertificateManager::Certificate",
                Properties={}
            ),
            "Resource21": CfnTemplateResourceDefinition(
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/ResourceGroup2/resource21"
                }), # type: ignore
                Type="AWS::EC2::Instance",
                Properties={}
            ),
            "Resource22": CfnTemplateResourceDefinition(
                Metadata=CfnTemplateResourceMetadataDefinition(**{
                    "aws:cdk:path": "some-stack/ResourceGroup2/resource22"
                }), # type: ignore
                Type="AWS::CertificateManager::Certificate",
                Properties={}
            )
        },
    )
    tree = CfnTemplateTree(
        template_source=CfnTemplateSource("/tmp/template.yaml", context=AppContext(log_level=logging.DEBUG)),
        definition=definition,
        spec_repository=spec_repository,
        context=context
    )
    toc = generator.table_of_contents(tree)
    assert toc == expected_toc

@pytest.mark.parametrize("version,description,transform,e_version,e_description,e_transform", [
    ("2012-10", "template-descirption", "t1", "2012-10", "template-descirption", "t1"),
    ("2012-10", "template-descirption", ["t1", "t2"], "2012-10", "template-descirption", "<ul><li>t1</li><li>t2</li></ul>"),
    (None, None, [], "-", "-", "-"),
])
def test_CfnMarkdownDocumentGenerator_overview(
    version:Optional[str], description:Optional[str], transform:Union[str, List[str]],
    e_version:str, e_description:str, e_transform:str,
    cfn_template_tree:CfnTemplateTree,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
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
def test_CfnMarkdownDocumentGenerator_description(
        cfn_docgen_description:Optional[str], e_cfn_docgen_description:str,
        cfn_template_tree:CfnTemplateTree,
        context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    cfn_template_tree.cfn_docgen_description = cfn_docgen_description
    description = generator.description(cfn_template_tree)
    assert description == e_cfn_docgen_description

@pytest.mark.parametrize("paramters_node,e_parameters",[
    (
        # without parameter groups
        CfnTemplateParametersNode(
            context=AppContext(log_level=logging.DEBUG),
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
            "### param1",
            "",
            "param1-description",
            "",
            "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|",
            "|-|-|-|-|-|-|-|-|-|-|",
            "|String|s1|<ul><li>s1</li><li>s2</li></ul>|allowedpattern|true|-|-|2|10|constraintdescription|",
            "",
            "### param2",
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
            context=AppContext(log_level=logging.DEBUG),
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
            context=AppContext(log_level=logging.DEBUG),
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
            "### param1",
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
            context=AppContext(log_level=logging.DEBUG),
            definitions={},
            parameter_groups=[]
        ),
        "\n".join([
            "## Parameters",
        ])
    )
])
def test_CfnMarkdownDocumentGenerator_parameters(
    paramters_node:CfnTemplateParametersNode, e_parameters:str,
    cfn_template_tree:CfnTemplateTree,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    cfn_template_tree.parameters_node = paramters_node

    parameters = generator.parameters(cfn_template_tree)
    assert parameters == e_parameters

@pytest.mark.parametrize("mappings_node,e_mappings", [
    (
        CfnTemplateMappingsNode(
            context=AppContext(log_level=logging.DEBUG),
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
            context=AppContext(log_level=logging.DEBUG),
            definitions={},
            descriptions={}
        ),
        "\n".join([
            "## Mappings",
        ])
    )
])
def test_CfnMarkdownDocumentGenerator_mappings(
        mappings_node:CfnTemplateMappingsNode, e_mappings:str,
        cfn_template_tree:CfnTemplateTree,
        context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    cfn_template_tree.mappings_node = mappings_node
    
    mappings = generator.mappings(cfn_template_tree)
    assert mappings == e_mappings


@pytest.mark.parametrize("conditions_node,e_conditions", [
    (
        CfnTemplateConditionsNode(
            context=AppContext(log_level=logging.DEBUG),
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
            context=AppContext(log_level=logging.DEBUG),
            definitions={},
            descriptions={}
        ),
        "\n".join([
            "## Conditions",
        ])
    )
])
def test_CfnMarkdownDocumentGenerator_conditions(
        conditions_node:CfnTemplateConditionsNode, e_conditions:str,
        cfn_template_tree:CfnTemplateTree,
        context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
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
    ),
    (
        "${string}",
        "\\${string}"
    ),
    (
        {"Sub": "${string}"},
        '{<br/>&nbsp;&nbsp;"Sub":&nbsp;"\\${string}"<br/>}',
    ),
    (
        "string|string",
        "string\\|string"
    ),
    (
        {"Ref": "string|string"},
        '{<br/>&nbsp;&nbsp;"Ref":&nbsp;"string\\|string"<br/>}',
    ),
    (
        "日本語",
        "日本語"
    ),
    (
        {"Ref": "日本語"},
        '{<br/>&nbsp;&nbsp;"Ref":&nbsp;"日本語"<br/>}',
    ),
    (
        "List<AWS::EC2::VPC>",
        "List\\<AWS::EC2::VPC\\>"
    ),
    (
        {"Ref": "List<AWS::EC2::VPC>"},
        '{<br/>&nbsp;&nbsp;"Ref":&nbsp;"List\\<AWS::EC2::VPC\\>"<br/>}',
    )

])
def test_CfnMarkdownDocumentGenerator_dump_json(
    j:Any,expected:str,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)

    dumped = generator._dump_json(j) # type: ignore
    assert dumped == expected
    

@pytest.mark.parametrize("rules_node,e_rules",[
    (
        CfnTemplateRulesNode(
            context=AppContext(log_level=logging.DEBUG),
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
            context=AppContext(log_level=logging.DEBUG),
            definitions={},
            descriptions={},
        ),
        "\n".join([
            "## Rules",
        ])
    )
])
def test_CfnMarkdownDocumentGenerator_rules(
    rules_node:CfnTemplateRulesNode, e_rules:str, 
    cfn_template_tree:CfnTemplateTree,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    cfn_template_tree.rules_node = rules_node

    rules = generator.rules(cfn_template_tree)
    assert rules == e_rules


@pytest.mark.parametrize("resources_node,e_resources", [
    (
        CfnTemplateResourcesNode(
            context=AppContext(log_level=logging.DEBUG),
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
                context=AppContext(log_level=logging.DEBUG),
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                loader_factory=specification_loader_factory,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=AppContext(log_level=logging.DEBUG)),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            ),
            resource_groups={},
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
            context=AppContext(log_level=logging.DEBUG),
            definitions={},
            spec_repository=CfnSpecificationRepository(
                context=AppContext(log_level=logging.DEBUG),
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                loader_factory=specification_loader_factory,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=AppContext(log_level=logging.DEBUG)),
                recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
            ),
            resource_groups={},
        ),
        "\n".join([
            "## Resources",
        ])
    )
])
def test_CfnMarkdownDocumentGenerator_resources(
        resources_node:CfnTemplateResourcesNode, e_resources:str,
        cfn_template_tree:CfnTemplateTree,
        context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    cfn_template_tree.resources_node = resources_node

    resources = generator.resources(cfn_template_tree)
    assert resources == e_resources

def test_CfnMarkdownDocumentGenerator_flatten_properties(context:AppContext):
    cfn_template_tree = CfnTemplateResourcesNode(
        context=context,
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
            context=context,
            source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
            loader_factory=specification_loader_factory,
            cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context,),
            recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        ),
        resource_groups={},
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

    generator = CfnMarkdownDocumentGenerator(context=context,)

    properties = generator._flatten_properties_node( # type: ignore
        cfn_template_tree.group_nodes[cfn_template_tree.group_name_for_independent_resources].resource_nodes["Instance"].properties_node,
    )
    assert len(properties) == len(expected)
    for p, e in zip(properties, expected):
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
def test_CfnMarkdownDocumentGenerator_simplify_jsonpath(
    jsonpath:str, expected:str,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context,)
    path = generator._simplify_jsonpath(jsonpath) # type: ignore
    assert path == expected


@pytest.mark.parametrize("outputs_node,e_outputs", [
    (
        CfnTemplateOutputsNode(
            context=AppContext(log_level=logging.DEBUG),
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
            context=AppContext(log_level=logging.DEBUG),
            definitions={}
        ),
        "\n".join([
            "## Outputs",
        ])
    )
])
def test_CfnMarkdownDocumentGenerator_outputs(
    outputs_node:CfnTemplateOutputsNode, e_outputs:str,
    cfn_template_tree:CfnTemplateTree,
    context:AppContext,
):
    cfn_template_tree.outputs_node = outputs_node
    generator = CfnMarkdownDocumentGenerator(context=context)
    outputs = generator.outputs(cfn_template_tree)
    assert outputs == e_outputs

@pytest.mark.parametrize("tree,e_template", [
    (
        CfnTemplateTree(
            context=AppContext(log_level=logging.DEBUG),
            template_source=CfnTemplateSource("template.yaml", context=AppContext(log_level=logging.DEBUG)),
            definition=CfnTemplateDefinition(
                Resources={"resource1": CfnTemplateResourceDefinition(
                    Type="AWS::EC2::Instance",
                    Properties={},
                )}
            ),
            spec_repository=CfnSpecificationRepository(
                context=AppContext(log_level=logging.DEBUG),
                loader_factory=specification_loader_factory,
                source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
                cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=AppContext(log_level=logging.DEBUG)),
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
def test_CfnMarkdownDocumentGenerator_generate(
    tree:CfnTemplateTree, e_template:str,
    context:AppContext,
):
    generator = CfnMarkdownDocumentGenerator(context=context)
    template = generator.generate(tree)
    header = generator.header()

    assert template == header + "\n" + e_template

