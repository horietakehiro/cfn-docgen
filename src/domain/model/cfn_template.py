from __future__ import annotations
import json

from typing import Any, List, Literal, Mapping, Optional
from xmlrpc.client import Boolean
from pydantic import BaseModel, PositiveInt

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
class CfnTemplateOutpusDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"""
    Description: Optional[str] = None
    Value: Any
    Export: Optional[CfnTemplateOutputExportDefinition] = None

class CfnTemplateDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html"""
    Description: Optional[str] = None
    AWSTemplateFormatVersion: Optional[str] = None
    Metadata: Optional[Mapping[str, Any]] = None
    Parameters: Optional[Mapping[str, CfnTemplateParameterDefinition]] = None
    Rules: Optional[Mapping[str, CfnTemplateRuleDefinition]] = None
    Mappings: Optional[Mapping[str, Mapping[str, Mapping[str, Any]]]] = None
    Conditions: Optional[Mapping[str, Any]] = None
    Transform: Optional[str | List[str]] = None
    Resources: Mapping[str, CfnTemplateResourceDefinition]
    Outputs: Optional[Mapping[str, CfnTemplateOutpusDefinition]] = None

    @classmethod
    def from_string(cls, template:str) -> CfnTemplateDefinition:
        d  = json.loads(template)
        return CfnTemplateDefinition(**d)

# class CfnTemplate:

#     def __init__(self, definition:CfnTemplateDefinition, spec_repository:) -> None:
#         pass