from __future__ import annotations
import json

from typing import Any, List, Literal, Mapping, Optional, Tuple
from xmlrpc.client import Boolean
from pydantic import BaseModel, Field, PositiveInt

class CfnTemplateParameterDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"""
    AllowedPattern: Optional[str] = None
    AllowedValues: Optional[List[str] | List[int]] = None
    ConstraintDescription: Optional[str] = None
    Default: Optional[str | int | List[str] | List[int]] = None
    Description: Optional[str] = None
    MaxLength: Optional[PositiveInt] = None
    MinLength: Optional[PositiveInt] = None
    MaxValue: Optional[int] = None
    MinValue: Optional[int] = None
    NoEcho: Boolean = False
    Type: Literal[
        "String", "Number", "List<Number>", "CommaDelimitedList",
        "AWS::EC2::AvailabilityZone::Name",
        "AWS::EC2::Image::Id",
        "AWS::EC2::Instance::Id",
        "AWS::EC2::KeyPair::KeyName",
        "AWS::EC2::SecurityGroup::GroupName",
        "AWS::EC2::SecurityGroup::Id",
        "AWS::EC2::Subnet::Id",
        "AWS::EC2::Volume::Id",
        "AWS::EC2::VPC::Id",
        "AWS::Route53::HostedZone::Id",
        "List<AWS::EC2::AvailabilityZone::Name>",
        "List<AWS::EC2::Image::Id>",
        "List<AWS::EC2::Instance::Id>",
        "List<AWS::EC2::SecurityGroup::GroupName>",
        "List<AWS::EC2::SecurityGroup::Id>",
        "List<AWS::EC2::Subnet::Id>",
        "List<AWS::EC2::Volume::Id>",
        "List<AWS::EC2::VPC::Id>",
        "List<AWS::Route53::HostedZone::Id>",
        "AWS::SSM::Parameter::Name",
        "AWS::SSM::Parameter::Value<String>",
        "AWS::SSM::Parameter::Value<List<String>>",
        "AWS::SSM::Parameter::Value<CommaDelimitedList>",
        "AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>",
        "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
        "AWS::SSM::Parameter::Value<AWS::EC2::Instance::Id>",
        "AWS::SSM::Parameter::Value<AWS::EC2::KeyPair::KeyName>",
        "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::GroupName>",
        "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>",
        "AWS::SSM::Parameter::Value<AWS::EC2::Subnet::Id>",
        "AWS::SSM::Parameter::Value<AWS::EC2::Volume::Id>",
        "AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>",
        "AWS::SSM::Parameter::Value<AWS::Route53::HostedZone::Id>",
        "AWS::SSM::Parameter::Value<List<AWS::EC2::AvailabilityZone::Name>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::Image::Id>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::Instance::Id>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::KeyPair::KeyName>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::GroupName>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::Id>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::Volume::Id>>"
        "AWS::SSM::Parameter::Value<List<AWS::EC2::VPC::Id>>"
        "AWS::SSM::Parameter::Value<List<AWS::Route53::HostedZone::Id>>"
    ]

class CfnTemplateMetadataCfnDocgenDefinition(BaseModel):
    Description: Optional[str] = None
    Mappings: Mapping[str, str] = {}
    Conditions: Mapping[str, str] = {}
    Rules: Mapping[str, str] = {}

class CfnTemplateMetadataParameterGroupLabel(BaseModel):
    default: str
class CfnTemplateMetadataParameterGroup(BaseModel):
    Label: CfnTemplateMetadataParameterGroupLabel
    Parameters: List[str]

class CfnTemplateMetadataInterface(BaseModel):
    ParameterGroups: List[CfnTemplateMetadataParameterGroup]
    ParameterLabels: Mapping[str, CfnTemplateMetadataParameterGroupLabel]

class CfnTemplateMetadataDefinition(BaseModel):
    aws_cloudformation_interface:CfnTemplateMetadataInterface = Field(default={}, alias="AWS::CloudFormation::Interface")
    CfnDocgen: Optional[CfnTemplateMetadataCfnDocgenDefinition] = None

class CfnTemplateRuleAssertDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/rules-section-structure.html"""
    Assert: Mapping[Any, Any]
    AssertDescription: str

class CfnTemplateRuleDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/rules-section-structure.html"""
    RuleCondition: Optional[Mapping[Any, Any]] = None
    Assertions: List[CfnTemplateRuleAssertDefinition]

# class CfnTemplateMappingDefinition(BaseModel):
#     """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html"""


class CfnTemplateResourceDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html and https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-product-attribute-reference.html"""
    Type: str
    Metadata: Optional[Mapping[str, Any]] = None
    DependsOn: Optional[List[str]] = None
    Properties: Mapping[str, Any]
    CreationPolicy: Optional[Mapping[str, Any]] = None
    DeletionPolicy: Literal["Delete", "Retain", "RetainExceptOnCreate", "Snapshot"] = "Delete"
    UpdatePolicy: Optional[Mapping[str, Any]] = None
    UpdateReplacePolicy: Literal["Delete", "Retain", "Snapshot"] = "Delete"

class CfnTemplateOutputExportDefinition(BaseModel):
    Name: str | Mapping[str, Any]
class CfnTemplateOutputDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"""
    Description: Optional[str] = None
    Value: Any
    Export: Optional[CfnTemplateOutputExportDefinition] = None
    Condition: Optional[str] = None

class CfnTemplateDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html"""
    Description: Optional[str] = None
    AWSTemplateFormatVersion: Optional[str] = None
    Metadata: Optional[CfnTemplateMetadataDefinition] = None
    Parameters: Mapping[str, CfnTemplateParameterDefinition] = {}
    Rules: Mapping[str, CfnTemplateRuleDefinition] = {}
    Mappings: Mapping[str, Mapping[str, Mapping[str, Any]]] = {}
    Conditions: Mapping[str, Any] = {}
    Transform: str | List[str] = []
    Resources: Mapping[str, CfnTemplateResourceDefinition]
    Outputs: Mapping[str, CfnTemplateOutputDefinition] = {}

    @classmethod
    def from_string(cls, template:str) -> CfnTemplateDefinition:
        d  = json.loads(template)
        return CfnTemplateDefinition(**d)


class CfnTemplateParameter:
    
    def __init__(self, name:str, template_definition:CfnTemplateDefinition) -> None:
        self.name = name
        self.definition = template_definition.Parameters.get(name, None)
        
        self.group = self.get_parameter_group(name, template_definition)

    def get_parameter_group(self, name:str, template_definition:CfnTemplateDefinition) -> Optional[str]:
        metadata = template_definition.Metadata
        if metadata is None:
            return
        interface = metadata.aws_cloudformation_interface
        for group in interface.ParameterGroups:
            if name in group.Parameters:
                return group.Label.default
        return

class CfnTemplateMapping:

    def __init__(self, name:str, template_definition:CfnTemplateDefinition) -> None:
        self.name = name
        self.definition = template_definition.Mappings.get(name, None)

        self.description = self.get_description(name, template_definition)

    def get_description(self, name:str, template_definition:CfnTemplateDefinition) -> Optional[str]:
        metadata = template_definition.Metadata
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Mappings.get(name, None)

class CfnTemplateCondition:

    def __init__(self, name:str, template_definition:CfnTemplateDefinition) -> None:
        self.name = name
        self.definition = template_definition.Conditions.get(name, None)

        self.description = self.get_description(name, template_definition)
    
    def get_description(self, name:str, template_definition:CfnTemplateDefinition) -> Optional[str]:
        metadata = template_definition.Metadata
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Conditions.get(name, None)

class CfnTemplateRule:

    def __init__(self, name:str, template_definition:CfnTemplateDefinition) -> None:
        self.name = name
        self.definition = template_definition.Rules.get(name, None)

        self.description = self.get_description(name, template_definition)
        
    def get_description(self, name:str, template_definition:CfnTemplateDefinition) -> Optional[str]:
        metadata = template_definition.Metadata
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Rules.get(name, None)


class CfnTemplate:
    def __init__(self, filepath:str, definition:CfnTemplateDefinition) -> None:
        self.filepath = filepath
        self.definition = definition
        self.parameters = [
            CfnTemplateParameter(name, definition) for name in definition.Parameters.keys()
        ]
        self.mappings = [
            CfnTemplateMapping(name, definition) for name in definition.Mappings.keys()
        ]
        self.conditions = [
            CfnTemplateCondition(name, definition) for name in definition.Conditions.keys()
        ]
        self.rules = [
            CfnTemplateRule(name, definition) for name in definition.Rules.keys()
        ]

    def get_parameters_by_group(self, ) -> Tuple[Mapping[str, List[CfnTemplateParameter]], List[CfnTemplateParameter]]:
        parameters_by_group:Mapping[str, List[CfnTemplateParameter]] = {}
        ungrouped_parameters:List[CfnTemplateParameter] = []
        for parameter in self.parameters:
            group = parameter.group
            if group is None:
                ungrouped_parameters.append(parameter)
                continue
            if parameters_by_group.get(group, None) is None:
                parameters_by_group[group] = [parameter]
            else:
                parameters_by_group[group].append(parameter)
        
        return parameters_by_group, ungrouped_parameters

    def get_mapping_description(self, name:str) -> Optional[str]:
        for mapping in self.mappings:
            if mapping.name == name:
                return mapping.description
        return None
    
    def get_condition_description(self, name:str) -> Optional[str]:
        for condition in self.conditions:
            if condition.name == name:
                return condition.description
        
        return None
    
    def get_rule_description(self, name:str) -> Optional[str]:
        for rule in self.rules:
            if rule.name == name:
                return rule.description
            
        return None