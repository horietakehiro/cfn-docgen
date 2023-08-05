from __future__ import annotations
import json

from typing import Any, List, Literal, Mapping, Optional, Tuple
from xmlrpc.client import Boolean
from pydantic import BaseModel, Field, PositiveInt
from domain.model.cfn_specification import CfnSpecificationPropertyType

from domain.ports.cfn_specification_repository import ICfnSpecificationRepository

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

class CfnTemplateResourceMetadataCfnDocgenDefinition(BaseModel):
    Description: Optional[str] = None
    Properties: Optional[Mapping[str, Any]] = None

class CfnTemplateResourceMetadataDefinition(BaseModel):
    CfnDocgen: Optional[CfnTemplateResourceMetadataCfnDocgenDefinition] = None

CfnTemplateResourcePropertyPrimitiveTypeDefinition = str | int | float | bool
CfnTemplateResourcePropertyListTypeDefinition = List[
    'CfnTemplateResourcePropertyPrimitiveTypeDefinition' | 'CfnTemplateResourcePropertyListTypeDefinition' | 'CfnTemplateResourcePropertyMapTypeDefinition'
]
CfnTemplateResourcePropertyMapTypeDefinition = Mapping[
    str, 'CfnTemplateResourcePropertyPrimitiveTypeDefinition' | 'CfnTemplateResourcePropertyListTypeDefinition' | 'CfnTemplateResourcePropertyMapTypeDefinition'
]
CfnTemplateResourcePropertyDefinition = CfnTemplateResourcePropertyPrimitiveTypeDefinition | CfnTemplateResourcePropertyMapTypeDefinition | CfnTemplateResourcePropertyListTypeDefinition

class CfnTemplateResourceDefinition(BaseModel):
    """based on https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html and https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-product-attribute-reference.html"""
    Type: str
    Metadata: Optional[CfnTemplateResourceMetadataDefinition] = None
    DependsOn: Optional[List[str]] = None
    Condition: Optional[str] = None
    Properties: Mapping[str, CfnTemplateResourcePropertyDefinition]
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
    
    def __init__(self, name:str, definition:CfnTemplateParameterDefinition, metadata:CfnTemplateMetadataDefinition|None) -> None:
        self.name = name
        self.definition = definition
        
        self.group = self.get_parameter_group(name, metadata)

    def get_parameter_group(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
        if metadata is None:
            return
        interface = metadata.aws_cloudformation_interface
        for group in interface.ParameterGroups:
            if name in group.Parameters:
                return group.Label.default
        return

class CfnTemplateMapping:

    def __init__(self, name:str, definition:Mapping[str, Mapping[str, Mapping[str, Any]]], metadata:CfnTemplateMetadataDefinition|None) -> None:
        self.name = name
        self.definition = definition

        self.description = self.get_description(name, metadata)

    def get_description(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Mappings.get(name, None)

class CfnTemplateCondition:

    def __init__(self, name:str, definition:Mapping[str, Any], metadata:CfnTemplateMetadataDefinition|None) -> None:
        self.name = name
        self.definition = definition

        self.description = self.get_description(name, metadata)
    
    def get_description(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Conditions.get(name, None)

class CfnTemplateRule:

    def __init__(self, name:str, definition:CfnTemplateRuleDefinition, metadata:CfnTemplateMetadataDefinition|None) -> None:
        self.name = name
        self.definition = definition

        self.description = self.get_description(name, metadata)
        
    def get_description(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Rules.get(name, None)

class CfnTemplateResourceProperty:

    def __init__(
            self, prop_name:str, prop_type:str, definition:Optional[CfnTemplateResourcePropertyDefinition], spec_repository:ICfnSpecificationRepository,
            parent_resource_type:str, parent_prop_name:Optional[str]=None, index:Optional[int]=None, depth:int=0,
    ) -> None:
        self.name = prop_name
        self.type = prop_type
        self.definition = definition
        spec = spec_repository.get_property_spec(f"{parent_resource_type}.{prop_type}")
        assert spec is not None, f"Invalid property type : {parent_resource_type}/{prop_type}"
        self.spec = spec
        self.parent_resource_type = parent_resource_type
        self.parent_prop_name = parent_prop_name
        self.index = index
        self.depth = depth

        self.type_representation = self.determine_type_representation()

        self.properties = self.add_child_props(spec_repository)

    def determine_type_representation(self, ) -> str:
        if self.spec.PrimitiveType is not None:
            return self.spec.PrimitiveType
        if self.spec.PrimitiveItemType is not None and self.spec.Type is not None:
            return f"{self.spec.Type} of {self.spec.PrimitiveItemType}"
        if self.spec.ItemType is not None and self.spec.Type is not None:
            return f"{self.spec.Type} of {self.spec.ItemType}"
        if self.spec.Type is not None:
            return self.spec.Type
        
        return "N/A"

    def add_child_props(self, spec_repository:ICfnSpecificationRepository) -> List[CfnTemplateResourceProperty] | None:
        if self.spec.Properties is None:
            return None
        for child_name, child_property in self.spec.Properties.items():

        # if self.spec.PrimitiveType is not None or self.spec.PrimitiveItemType is not None: # it is a bottom of properties
        #     return None

        # if self.spec.ItemType is not None and (self.spec.Type is not None and self.spec.Type.lower() == "list"):
        #     definition_list:CfnTemplateResourcePropertyListTypeDefinition = self.definition if isinstance(self.definition, list) else []
        #     return [
        #         CfnTemplateResourceProperty(
        #             prop_name=self.spec.ItemType, prop_type=self.spec.ItemType, definition=definition, spec_repository=spec_repository,
        #             parent_resource_type=self.parent_resource_type, parent_prop_name=self.name,
        #             index=i, depth=self.depth+1
        #         ) for i, definition in enumerate(definition_list)
        #     ]
        # if self.spec.ItemType is not None and (self.spec.Type is not None and self.spec.Type.lower() == "map"):
        #     definition_map:CfnTemplateResourcePropertyMapTypeDefinition = self.definition if isinstance(self.definition, dict) else {}
        #     return [
        #         CfnTemplateResourceProperty(
        #             prop_name=name, prop_type=self.spec.ItemType, definition=definition, spec_repository=spec_repository,
        #             parent_resource_type=self.parent_resource_type,parent_prop_name=self.name,
        #             index=None, depth=self.depth+1
        #         ) for name, definition, in definition_map.items()
        #     ]
        
        # if self.spec.Type is not None:
        #     return [
        #         CfnTemplateResourceProperty(
        #         prop_name=self.spec.Type, prop_type=self.spec.Type, 
        #         )
        #     ]



class CfnTemplateResource:

    def __init__(self, name:str, definition:CfnTemplateResourceDefinition, spec_repository:ICfnSpecificationRepository) -> None:
        self.name = name
        self.definition = definition
        self.description = self.get_description(name, definition)

        self.spec = spec_repository.get_resource_spec(self.definition.Type)

        self.properties:List[CfnTemplateResourceProperty] = []
        if self.spec is not None:
            self.properties = [
                CfnTemplateResourceProperty(
                    prop_name=name, prop_type=name, definition=self.definition.Properties.get(name, None), spec_repository=spec_repository,
                    parent_resource_type=self.definition.Type, parent_prop_name=None, index=None, depth=0,
                ) for name in self.spec.Properties.keys()
            ]

    def get_description(self, name:str, definition:CfnTemplateResourceDefinition) -> Optional[str]:
        metadata = definition.Metadata
        if metadata is None:
            return
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return
        return cfn_docgen.Description

class CfnTemplateOutput:

    def __init__(self, name:str, definition:CfnTemplateOutputDefinition) -> None:
        self.name = name
        self.definition = definition

class CfnTemplate:
    def __init__(self, filepath:str, definition:CfnTemplateDefinition, spec_repository:ICfnSpecificationRepository) -> None:
        self.filepath = filepath
        self.definition = definition
        self.parameters = [
            CfnTemplateParameter(name, definition.Parameters[name], definition.Metadata) for name in definition.Parameters.keys()
        ]
        self.mappings = [
            CfnTemplateMapping(name, definition.Mappings[name], definition.Metadata) for name in definition.Mappings.keys()
        ]
        self.conditions = [
            CfnTemplateCondition(name, definition.Conditions[name], definition.Metadata) for name in definition.Conditions.keys()
        ]
        self.rules = [
            CfnTemplateRule(name, definition.Rules[name], definition.Metadata) for name in definition.Rules.keys()
        ]
        self.resources = [
            CfnTemplateResource(name, definition.Resources[name], spec_repository) for name in definition.Resources.keys()
        ]
        self.outputs = [
            CfnTemplateOutput(name, definition.Outputs[name]) for name in definition.Outputs.keys()
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

    # def get_mapping_description(self, name:str) -> Optional[str]:
    #     for mapping in self.mappings:
    #         if mapping.name == name:
    #             return mapping.description
    #     return None
    
    # def get_condition_description(self, name:str) -> Optional[str]:
    #     for condition in self.conditions:
    #         if condition.name == name:
    #             return condition.description
        
    #     return None
    
    # def get_rule_description(self, name:str) -> Optional[str]:
    #     for rule in self.rules:
    #         if rule.name == name:
    #             return rule.description
            
    #     return None
    
    # def get_resource_description(self, name:str) -> Optional[str]:
    #     for resource in self.resources:
    #         if resource.name == name:
    #             return resource.description
    #         return None