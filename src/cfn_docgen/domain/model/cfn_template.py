from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import itertools
import json
import os
from jsonpath_ng import parse # type: ignore

from typing import Any, List, Literal, Mapping, Optional, Union, cast
from pydantic import BaseModel, Field, PositiveInt
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationForResource, CfnSpecificationProperty, CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName, CfnSpecificationPropertyType

from cfn_docgen.domain.ports.cfn_specification_repository import ICfnSpecificationRepository

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
    NoEcho: bool = False
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
    ParameterGroups: List[CfnTemplateMetadataParameterGroup] = []
    ParameterLabels: Mapping[str, CfnTemplateMetadataParameterGroupLabel] = {}

class CfnTemplateMetadataDefinition(BaseModel):
    aws_cloudformation_interface:Optional[CfnTemplateMetadataInterface] = Field(default=None, alias="AWS::CloudFormation::Interface")
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


    def get_resource_description(self, ) -> Optional[str]:
        return self.Description

    def get_property_description_by_json_path(self, json_path:str) -> Optional[str]:
        if self.Properties is None:
            return None
        jsonpath_expr = parse(json_path) # type: ignore
        descriptions:List[Any] = [f.value for f in jsonpath_expr.find(self.Properties)] # type: ignore
        if len(descriptions) != 1:
            return None
        description = descriptions[0]
        if not isinstance(description, str):
            return None
        return description

class CfnTemplateResourceMetadataDefinition(BaseModel):
    CfnDocgen: Optional[CfnTemplateResourceMetadataCfnDocgenDefinition] = None
    aws_cdk_path: Optional[str] = Field(alias="aws:cdk:path", default=None)

CfnTemplateResourcePropertyDefinition = Union[
    str,int,float, bool, List[Any], Mapping[Any, Any]
]

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
    def from_string(cls, template:str, context:AppContext) -> CfnTemplateDefinition:
        try:
            return CfnTemplateDefinition(**json.loads(template))
        except Exception as ex:
            context.log_error(f"failed to instanciate CfnTemplateDefinition from string. {str(ex)}")
            raise ex

    def __get_cfn_docgen(self) -> Optional[CfnTemplateMetadataCfnDocgenDefinition]:
        metadata = self.Metadata
        if metadata is None:
            return None
        cfn_docgen = metadata.CfnDocgen
        return cfn_docgen

    def get_parameter_groups(self) -> List[CfnTemplateMetadataParameterGroup]:
        metadata = self.Metadata
        if metadata is None:
            return []
        interface = metadata.aws_cloudformation_interface
        if interface is None:
            return []
        return interface.ParameterGroups
    
    def get_cfn_docgen_description(self) -> Optional[str]:
        cfn_docgen = self.__get_cfn_docgen()
        if cfn_docgen is None:
            return None
        return cfn_docgen.Description
    def get_mapping_descriptions(self) -> Mapping[str, str]:
        cfn_docgen = self.__get_cfn_docgen()
        if cfn_docgen is None:
            return {}
        return cfn_docgen.Mappings
    def get_rule_descriptions(self) -> Mapping[str, str]:
        cfn_docgen = self.__get_cfn_docgen()
        if cfn_docgen is None:
            return {}
        return cfn_docgen.Rules
    def get_condition_descriptions(self) -> Mapping[str, str]:
        cfn_docgen = self.__get_cfn_docgen()
        if cfn_docgen is None:
            return {}
        return cfn_docgen.Conditions
    
    def get_resource_groups(self) -> Mapping[str, List[str]]:
        
        resource_groups:Mapping[str, List[str]] = defaultdict(list)
        for resource_id, resource_body in self.Resources.items():
            if resource_body.Metadata is None:
                continue
            if resource_body.Metadata.aws_cdk_path is None:
                continue
            # aws:cdk:path wll be like CdkWorkshopStack/BlogVpc/PrivateSubnet1/Subnet
            paths = resource_body.Metadata.aws_cdk_path.split("/")
            if len(paths) < 2:
                continue
            resource_groups[paths[1]].append(resource_id)

        return resource_groups


class CfnTemplateParametersNode:

    group_name_for_independent_parameters = "__CFN_DOCGEN_INDEPENDENT_PARAMETERS__"

    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateParameterDefinition],
        parameter_groups:List[CfnTemplateMetadataParameterGroup],
        context:AppContext,
    ) -> None:
        
        self.group_nodes:Mapping[str, CfnTemplateParameterGroupNode] ={}
        for group in parameter_groups:
            try:
                self.group_nodes[group.Label.default] = CfnTemplateParameterGroupNode(
                    definitions={
                        param_name: definition 
                        for param_name, definition in definitions.items()
                        if param_name in group.Parameters
                    },
                    context=context,
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateParameterGroupNode for parameter group [{group.Label.default}]")
                continue

        try:
            parameter_names_in_groups = list(itertools.chain.from_iterable(
                [group.Parameters for group in parameter_groups]
            ))
            self.group_nodes[self.group_name_for_independent_parameters] = CfnTemplateParameterGroupNode(
                definitions={
                    param_name: definition for param_name, definition in definitions.items()
                    if param_name not in parameter_names_in_groups
                },
                context=context,
            )
        except Exception:
            context.log_warning(f"failed to build CfnTemplateParameterGroupNode for parameter group [{self.group_name_for_independent_parameters}]")


class CfnTemplateParameterGroupNode:
    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateParameterDefinition],
        context:AppContext,
    ) -> None:
        self.leaves:Mapping[str, CfnTemplateParameterLeaf] = {}
        for name, definition in definitions.items():
            try:
                self.leaves[name] = CfnTemplateParameterLeaf(definition=definition)
            except Exception:
                context.log_warning(f"failed to build CfnTemplateParameterLeaf for parameter [{name}]")
                continue

class CfnTemplateParameterLeaf:
    def __init__(self, definition:CfnTemplateParameterDefinition) -> None:
        self.definition = definition


class CfnTemplateMappingLeaf:
    def __init__(
        self, 
        definition:Mapping[str, Mapping[str, Any]],
        description:Optional[str],
    ) -> None:
        self.definition = definition
        self.description = description

class CfnTemplateMappingsNode:
    def __init__(
        self,
        definitions:Mapping[str, Mapping[str, Mapping[str, Any]]],
        descriptions:Mapping[str, str],
        context:AppContext,
    ) -> None:
        self.mapping_leaves:Mapping[str, CfnTemplateMappingLeaf] = {}
        for name, definition in definitions.items():
            try:
                self.mapping_leaves[name] = CfnTemplateMappingLeaf(
                    definition=definition,
                    description=descriptions.get(name)
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateMappingLeaf for mapping [{name}]")
                continue

class CfnTemplateConditionLeaf:
    def __init__(
        self,
        definition: Mapping[str, Any],
        description: Optional[str],
    ) -> None:
        self.definition = definition
        self.descirption = description

class CfnTemplateConditionsNode:
    def __init__(
        self,
        definitions: Mapping[str, Mapping[str, Any]],
        descriptions: Mapping[str, str],
        context:AppContext,
    ) -> None:
        self.condition_leaves:Mapping[str, CfnTemplateConditionLeaf] = {}
        for name, definition in definitions.items():
            try:
                self.condition_leaves[name] = CfnTemplateConditionLeaf(
                    definition=definition,
                    description=descriptions.get(name)
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateConditionLeaf for condition [{name}]")
                continue

class CfnTemplateRuleLeaf:
    def __init__(
        self,
        definition: CfnTemplateRuleDefinition,
        description: Optional[str]
    ) -> None:
        self.definition = definition
        self.description = description


class CfnTemplateRulesNode:
    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateRuleDefinition],
        descriptions:Mapping[str, str],
        context:AppContext,
    ) -> None:
        self.rule_leaves:Mapping[str, CfnTemplateRuleLeaf] = {}
        for name, definition in definitions.items():
            try:
                self.rule_leaves[name] = CfnTemplateRuleLeaf(
                    definition=definition,
                    description=descriptions.get(name),
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateRuleLeaf for rule [{name}]")
                continue

class CfnTemplateResourcePropertyLeaf:
    def __init__(
        self,
        definition:Optional[CfnTemplateResourcePropertyDefinition],
        property_spec:CfnSpecificationProperty,
        description:Optional[str],
        json_path:str,
    ) -> None:
        self.definition = definition
        self.spec = property_spec
        self.description = description
        self.json_path = json_path

    def type_repr(self,) -> str:
        if self.spec.PrimitiveType is not None:
            return self.spec.PrimitiveType
        if self.spec.PrimitiveItemType is not None and self.spec.Type is not None:
            return f"{self.spec.Type} of {self.spec.PrimitiveItemType}"
        if self.spec.ItemType is not None and self.spec.Type is not None:
            return f"{self.spec.Type} of {self.spec.ItemType}"
        if self.spec.Type is not None:
            return self.spec.Type
        return "-"

class CfnTemplateResourcePropertyNode:
    def __init__(
        self,
        definitions:Optional[CfnTemplateResourcePropertyDefinition],
        resource_property_spec:Optional[CfnSpecificationProperty],
        description:Optional[str],
        properties_spec:Mapping[str, CfnSpecificationProperty],
        json_path:str,
        cfn_docgen_metadata:Optional[CfnTemplateResourceMetadataCfnDocgenDefinition],
        property_specs:Mapping[str, CfnSpecificationPropertyType],
        resource_info:ResourceInfo,
        context:AppContext,
    ) -> None:
        self.property_nodes:Mapping[
            str, # e.g. CpuOptions in AWS::EC2::Instance
            CfnTemplateResourcePropertyNode # its node
        ] = {}
        self.property_nodes_map:Mapping[
            str, # e.g. CustomResponseBodies in AWS::WAFv2::WebACL
            Mapping[
                str, # its key
                CfnTemplateResourcePropertyNode # its node
            ]
        ] = {}
        self.property_nodes_list:Mapping[
            str, # e.g. BlockDeviceMappings in AWS::EC2::Instance
            List[CfnTemplateResourcePropertyNode] # its list of node
        ] = {}
        self.property_leaves:Mapping[
            str, # e.g. ImageId in AWS::EC2::Instance
            CfnTemplateResourcePropertyLeaf # its definition
        ] = {}

        self.description = description
        self.json_path = json_path
        self.spec = resource_property_spec
        self.has_leaves = definitions is not None


        for property_name, property_spec in properties_spec.items():
            try:
                if (
                    property_spec.PrimitiveType is not None 
                    or property_spec.PrimitiveItemType is not None
                ):
                # e.g. CoreCount in AWS::EC2::Instance.CpuOptions (string primitive type)
                # or Value in AWS::EC2::Instance.AssociationParameter (list of string primitive item type)
                # or Options in AWS::ECS::Service.LogConfiguration (map of string primitive item type)
                    definition:Any = None
                    if definitions is not None and isinstance(definitions, dict):
                        definition = cast(Mapping[str, CfnTemplateResourcePropertyDefinition], definitions).get(property_name, None)
                    prop_json_path = f"{self.json_path}.{property_name}"
                    description = cfn_docgen_metadata.get_property_description_by_json_path(
                        json_path=prop_json_path,
                    ) if cfn_docgen_metadata is not None else None
                    if resource_info.is_recursive and definition is None:
                        continue
                    self.property_leaves[property_name] = CfnTemplateResourcePropertyLeaf(
                        definition=definition,
                        property_spec=property_spec,
                        description=description,
                        json_path=prop_json_path,
                    )
                    continue

            except Exception:
                context.log_warning(f"failed to build CfnTemplateResourcePropertyLeaf for property [{property_name}]")
                continue

            try:

                if property_spec.ItemType is not None:
                    if (
                        property_spec.Type is not None
                        and property_spec.Type.lower() == "list"
                    ):
                    # e.g. AssociationParameters in AWS::EC2::Instance.SsmAssociation
                        _property_spec = property_specs.get(
                            CfnSpecificationPropertyTypeName(f"{resource_info.type}.{property_spec.ItemType}", context).fullname
                        )
                        if _property_spec is None or _property_spec.Properties is None:
                            continue
                        definition_list:List[Any] = []
                        if definitions is not None and isinstance(definitions, dict):
                            definition_list = cast(Mapping[str, List[Any]], definitions).get(property_name, [None])
                        if not isinstance(definition_list, list): # type: ignore
                            raise ValueError
                        property_nodes_list:List[CfnTemplateResourcePropertyNode] = []
                        for i, definition in enumerate(definition_list):
                            # prop_name is Key, Value, ...
                            prop_json_path = f"{self.json_path}.{property_name}[{i}]"
                            description = cfn_docgen_metadata.get_property_description_by_json_path(
                                json_path=prop_json_path,
                            ) if cfn_docgen_metadata is not None else None
                            if resource_info.is_recursive and definition is None:
                                continue
                            property_nodes_list.append(CfnTemplateResourcePropertyNode(
                                definitions=definition,
                                resource_property_spec=property_spec,
                                description=description,
                                json_path=prop_json_path,
                                properties_spec=_property_spec.Properties,
                                property_specs=property_specs,
                                cfn_docgen_metadata=cfn_docgen_metadata,
                                resource_info=resource_info,
                                context=context,
                            ))
                        self.property_nodes_list[property_name] = property_nodes_list.copy()
                        continue

                    if (
                        property_spec.Type is not None
                        and property_spec.Type.lower() == "map"
                    ):
                    # e.g. RequestBodyAssociatedResourceTypeConfig in AWS::WAFv2::WebACL.AssociationConfig
                        
                        _property_spec = property_specs.get(
                            CfnSpecificationPropertyTypeName(f"{resource_info.type}.{property_spec.ItemType}", context).fullname
                        )
                        if _property_spec is None or _property_spec.Properties is None:
                            continue
                        definition_map:Mapping[str, Any] = {}
                        if definitions is not None and isinstance(definitions, dict):
                            definition_map = cast(Mapping[str, Mapping[str, Any]], definitions).get(property_name, {"key": None})
                        if not isinstance(definition_map, dict): # type: ignore
                            raise ValueError
                        property_nodes_map:Mapping[str, CfnTemplateResourcePropertyNode] = {}
                        for key, definition in definition_map.items():
                            # prop_name is DefaultSizeInspectionLimit, ...
                            prop_json_path = f"{self.json_path}.{property_name}.{key}"
                            description = cfn_docgen_metadata.get_property_description_by_json_path(
                                json_path=prop_json_path
                            ) if cfn_docgen_metadata is not None else None
                            if resource_info.is_recursive and definition is None:
                                continue
                            property_nodes_map[key] = CfnTemplateResourcePropertyNode(
                                definitions=definition,
                                resource_property_spec=property_spec,
                                properties_spec=_property_spec.Properties,
                                property_specs=property_specs,
                                description=description,
                                json_path=prop_json_path,
                                cfn_docgen_metadata=cfn_docgen_metadata,
                                resource_info=resource_info,
                                context=context,
                            )
                        self.property_nodes_map[property_name] = property_nodes_map.copy()
                        continue

                # the rest is e.g. Ebs in AWS::EC2::Instance.BlockDeviceMapping
                _property_spec = property_specs.get(
                    CfnSpecificationPropertyTypeName(f"{resource_info.type}.{property_spec.Type}", context).fullname
                )
                if _property_spec is None and property_spec.Type == "Tag":
                    _property_spec = property_specs.get(
                        CfnSpecificationPropertyTypeName(property_spec.Type, context).fullname
                    )
                if _property_spec is None or _property_spec.Properties is None:
                    continue
                definition:Any = None
                if definitions is not None and isinstance(definitions, dict):
                    definition = cast(Mapping[str, Any], definitions).get(property_name, None)
                prop_json_path = f"{self.json_path}.{property_name}"
                description = cfn_docgen_metadata.get_property_description_by_json_path(
                    json_path=prop_json_path
                ) if cfn_docgen_metadata is not None else None
                if resource_info.is_recursive and definition is None:
                    continue
                self.property_nodes[property_name] = CfnTemplateResourcePropertyNode(
                    definitions=definition,
                    resource_property_spec=property_spec,
                    properties_spec=_property_spec.Properties,
                    property_specs=property_specs,
                    cfn_docgen_metadata=cfn_docgen_metadata,
                    resource_info=resource_info,
                    json_path=prop_json_path,
                    description=description,
                    context=context,
                )
                continue

            except Exception:
                context.log_warning(f"failed to build CfnTemplateResourcePropertyNode for property [{property_name}]")
                continue


class CfnTemplateResourcePropertiesNode:
    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateResourcePropertyDefinition],
        resource_property_specs:Mapping[str, CfnSpecificationProperty],
        property_specs:Mapping[str, CfnSpecificationPropertyType],
        cfn_docgen_metadata:Optional[CfnTemplateResourceMetadataCfnDocgenDefinition],
        resource_info:ResourceInfo,
        context:AppContext,

    ) -> None:
        self.property_nodes:Mapping[
            str, # e.g. CpuOptions in AWS::EC2::Instance
            CfnTemplateResourcePropertyNode # its node
        ] = {}
        self.property_nodes_map:Mapping[
            str, # e.g. CustomResponseBodies in AWS::WAFv2::WebACL
            Mapping[
                str, # its key
                CfnTemplateResourcePropertyNode # its node
            ]
        ] = {}
        self.property_nodes_list:Mapping[
            str, # e.g. BlockDeviceMappings in AWS::EC2::Instance
            List[CfnTemplateResourcePropertyNode] # its list of node
        ] = {}

        self.property_leaves:Mapping[
            str, # e.g. ImageId in AWS::EC2::Instance
            CfnTemplateResourcePropertyLeaf # its definition
        ] = {}

        self.json_path = "$"

        for property_name, resource_property_spec in resource_property_specs.items():
        # property_name is like ImageId, BlockDeviceMappings, CpuOptions, ... in AWS::EC2::Instance

            try:
                if (
                    resource_property_spec.PrimitiveType is not None 
                    or resource_property_spec.PrimitiveItemType is not None
                ):
                # e.g. ImageId in AWS::EC2::Instance (string primitive type)
                # or SecurityGroupIds in AWS::EC2::Instance (list of string primitive item type)
                # or Tags in AWS::MSK::Cluster (map of string primitive item type)
                    definition = definitions.get(property_name, None)
                    prop_json_path = f"{self.json_path}.{property_name}"
                    description = cfn_docgen_metadata.get_property_description_by_json_path(
                        json_path=prop_json_path,
                    ) if cfn_docgen_metadata is not None else None
                    if resource_info.is_recursive and definition is None:
                        continue
                    self.property_leaves[property_name] = CfnTemplateResourcePropertyLeaf(
                        definition=definition,
                        property_spec=resource_property_spec,
                        description=description,
                        json_path=prop_json_path,
                    )
                    continue
            except Exception:
                context.log_warning(f"failed to build CfnTemplateResourcePropertyLeaf for property [{property_name}]")
                continue

            try:
                if resource_property_spec.ItemType is not None:
                    if (
                        resource_property_spec.Type is not None
                        and resource_property_spec.Type.lower() == "list"
                    ):
                    # e.g. BlockDeviceMappings in AWS::EC2::Instance
                        property_spec = property_specs.get(
                            CfnSpecificationPropertyTypeName(f"{resource_info.type}.{resource_property_spec.ItemType}", context).fullname
                        )
                        if property_spec is None and resource_property_spec.ItemType == "Tag":
                            property_spec = property_specs.get(
                                CfnSpecificationPropertyTypeName(resource_property_spec.ItemType, context).fullname
                            )
                        if property_spec is None or property_spec.Properties is None:
                            continue
                        definition_list = definitions.get(property_name, [None])
                        if not isinstance(definition_list, list):
                            raise ValueError
                        property_nodes_list:List[CfnTemplateResourcePropertyNode] = []
                        for i, definition in enumerate(definition_list):
                            # prop_name is DeviceName, Ebs, ...
                            prop_json_path = f"{self.json_path}.{property_name}[{i}]"
                            description = cfn_docgen_metadata.get_property_description_by_json_path(
                                json_path=prop_json_path,
                            ) if cfn_docgen_metadata is not None else None
                            if resource_info.is_recursive and definition is None:
                                continue
                            property_nodes_list.append(CfnTemplateResourcePropertyNode(
                                definitions=definition,
                                resource_property_spec=resource_property_spec,
                                description=description,
                                json_path=prop_json_path,
                                properties_spec=property_spec.Properties,
                                property_specs=property_specs,
                                resource_info=resource_info,
                                cfn_docgen_metadata=cfn_docgen_metadata,
                                context=context,
                            ))
                        self.property_nodes_list[property_name] = property_nodes_list.copy()
                        continue

                    if (
                        resource_property_spec.Type is not None
                        and resource_property_spec.Type.lower() == "map"
                    ):
                    # e.g. CustomResponseBody in AWS::WAFv2::WebACL
                        
                        property_spec = property_specs.get(
                            CfnSpecificationPropertyTypeName(f"{resource_info.type}.{resource_property_spec.ItemType}", context).fullname
                        )
                        if property_spec is None or property_spec.Properties is None:
                            continue
                        definition_map = definitions.get(property_name, {"key": None})
                        if not isinstance(definition_map, dict):
                            raise ValueError
                        property_nodes_map:Mapping[str, CfnTemplateResourcePropertyNode] = {}
                        for key, definition in definition_map.items():
                            # for prop_name, prop_spec in property_spec.Properties.items():
                            # prop_name is ContentType, Content, ...
                            prop_json_path = f"{self.json_path}.{property_name}.{key}"
                            description = cfn_docgen_metadata.get_property_description_by_json_path(
                                json_path=prop_json_path
                            ) if cfn_docgen_metadata is not None else None
                            if resource_info.is_recursive and definition is None:
                                continue
                            property_nodes_map[key] = CfnTemplateResourcePropertyNode(
                                definitions=definition,
                                resource_property_spec=resource_property_spec,
                                description=description,
                                json_path=prop_json_path,
                                properties_spec=property_spec.Properties,
                                property_specs=property_specs,
                                resource_info=resource_info,
                                cfn_docgen_metadata=cfn_docgen_metadata,
                                context=context,
                            )
                        self.property_nodes_map[property_name] = property_nodes_map.copy()
                        continue

                # the rest is e.g. CpuOptions in AWS::EC2::Instance
                property_spec = property_specs.get(
                    CfnSpecificationPropertyTypeName(f"{resource_info.type}.{resource_property_spec.Type}", context).fullname
                )
                if property_spec is None or property_spec.Properties is None:
                    continue
                definition = definitions.get(property_name, None)
                prop_json_path = f"{self.json_path}.{property_name}"
                description = cfn_docgen_metadata.get_property_description_by_json_path(
                    json_path=prop_json_path
                ) if cfn_docgen_metadata is not None else None
                if resource_info.is_recursive and definition is None:
                    continue
                self.property_nodes[property_name] = CfnTemplateResourcePropertyNode(
                    definitions=definition,
                    resource_property_spec=resource_property_spec,
                    properties_spec=property_spec.Properties,
                    property_specs=property_specs,
                    resource_info=resource_info,
                    json_path=prop_json_path,
                    description=description,
                    cfn_docgen_metadata=cfn_docgen_metadata,
                    context=context,
                )
                continue

            except Exception:
                context.log_warning(f"failed to build CfnTemplateResourcePropertyNode for property [{property_name}]")
                continue


class CfnTemplateResourceNode:
    def __init__(
        self,
        definition:CfnTemplateResourceDefinition,
        specs:CfnSpecificationForResource,
        resource_info:ResourceInfo,
        context:AppContext,
    ) -> None:
        metadata = definition.Metadata
        cfn_docgen = metadata.CfnDocgen if metadata is not None else None

        self.description:Optional[str] = cfn_docgen.get_resource_description() if cfn_docgen is not None else None
        self.condition = definition.Condition
        self.creation_policy = definition.CreationPolicy
        self.update_policy =  definition.UpdatePolicy
        self.deletion_policy = definition.DeletionPolicy
        self.update_replace_policy = definition.UpdateReplacePolicy
        self.metadata = definition.Metadata
        self.depends_on:List[str] = definition.DependsOn if definition.DependsOn is not None else []
        self.type = resource_info.type

        self.spec = specs.ResourceSpec

        try:
            self.properties_node = CfnTemplateResourcePropertiesNode(
                definitions=definition.Properties,
                resource_property_specs=specs.ResourceSpec.Properties,
                property_specs=specs.PropertySpecs,
                cfn_docgen_metadata=cfn_docgen,
                resource_info=resource_info,
                context=context,
            )
        except Exception:
            context.log_warning("failed to build CfnTemplateResourcePropertiesNode")

    def __as_skelton(self, property_node:CfnTemplateResourcePropertyNode) -> Mapping[str, Any]:
        skelton:Mapping[str, Any] = {}
        for name, leaf in property_node.property_leaves.items():
            skelton[name] = leaf.type_repr()
        for name, node in property_node.property_nodes.items():
            skelton[name] = self.__as_skelton(node)
        for name, node in property_node.property_nodes_list.items():
            skelton[name] = [
                self.__as_skelton(n) for n in node
            ]
        for name, node in property_node.property_nodes_map.items():
            skelton[name] = {
                key: self.__as_skelton(value) for key, value in node.items()
            }
        return skelton


    def as_skelton(self) -> Mapping[str, Any]:
        skelton:Mapping[str, Any] = {}
        skelton["Type"] = self.type
        skelton["Metadata"] = {
            "CfnDocgen": {
                "Description" : "",
                "Properties": {},
            }
        }
        skelton["Properties"] = {}
        for name, leaf in self.properties_node.property_leaves.items():
            skelton["Properties"][name] = leaf.type_repr()
        for name, node in self.properties_node.property_nodes.items():
            skelton["Properties"][name] = self.__as_skelton(node)
        for name, node in self.properties_node.property_nodes_list.items():
            skelton["Properties"][name] = [
                self.__as_skelton(n) for n in node
            ]
        for name, node in self.properties_node.property_nodes_map.items():
            skelton["Properties"][name] = {
                key: self.__as_skelton(value) for key, value in node.items()
            }
        
        return skelton






class CfnTemplateResourceGroupNode:
    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateResourceDefinition],
        spec_repository:ICfnSpecificationRepository,
        context:AppContext,

    ) -> None:
        self.resource_nodes:Mapping[str, CfnTemplateResourceNode] = {}
        for name, definition in definitions.items():
            try:
                specs = spec_repository.get_specs_for_resource(CfnSpecificationResourceTypeName(definition.Type, context))
                resource_info=ResourceInfo(
                    type=definition.Type, 
                    is_recursive=spec_repository.is_recursive(CfnSpecificationResourceTypeName(definition.Type, context))
                )
                self.resource_nodes[name] = CfnTemplateResourceNode(
                    definition=definition, 
                    specs=specs,
                    resource_info=resource_info,
                    context=context,
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateResourceNode for resource [{name}]")

@dataclass
class ResourceInfo:
    type: str
    is_recursive: bool

class CfnTemplateResourcesNode:
    group_name_for_independent_resources = "__CFN_DOCGEN_INDEPENDENT_RESOURCES__"

    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateResourceDefinition],
        resource_groups:Mapping[str, List[str]],
        spec_repository:ICfnSpecificationRepository,
        context:AppContext,

    ) -> None:
        self.group_nodes:Mapping[str, CfnTemplateResourceGroupNode] = {}
        
        for group_name, resource_ids in resource_groups.items():
            try:
                self.group_nodes[group_name] = CfnTemplateResourceGroupNode(
                    definitions={
                        id_: d for id_, d in definitions.items()
                        if id_ in resource_ids
                    },
                    spec_repository=spec_repository,
                    context=context,
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateResourcesNode for resource group [{group_name}]")
                continue
        try:
            resource_ids_in_groups = list(itertools.chain.from_iterable(
                [resource_ids for resource_ids in resource_groups.values()]
            ))
            self.group_nodes[self.group_name_for_independent_resources] = CfnTemplateResourceGroupNode(
                definitions={
                    id_: d for id_, d in definitions.items()
                    if id_ not in resource_ids_in_groups
                },
                spec_repository=spec_repository,
                context=context,
            )
        except Exception:
            context.log_warning(f"failed to build CfnTemplateResourcesNode for resource group [{self.group_name_for_independent_resources}]")

        # self.resource_nodes:Mapping[str, CfnTemplateResourceNode] = {}
        # for name, definition in definitions.items():
        #     try:
        #         specs = spec_repository.get_specs_for_resource(CfnSpecificationResourceTypeName(definition.Type, context))
        #         resource_info=ResourceInfo(
        #             type=definition.Type, 
        #             is_recursive=spec_repository.is_recursive(CfnSpecificationResourceTypeName(definition.Type, context))
        #         )
        #         self.resource_nodes[name] = CfnTemplateResourceNode(
        #             definition=definition, 
        #             specs=specs,
        #             resource_info=resource_info,
        #             context=context,
        #         )
        #     except Exception:
        #         context.log_warning(f"failed to build CfnTemplateResourceNode for resource [{name}]")

class CfnTemplateOutputLeaf:
    def __init__(
        self,
        definition:CfnTemplateOutputDefinition    
    ) -> None:
        self.definition = definition

class CfnTemplateOutputsNode:
    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateOutputDefinition],
        context:AppContext,
    ) -> None:
        self.output_leaves:Mapping[str, CfnTemplateOutputLeaf] = {}
        for name, definition in definitions.items():
            try:
                self.output_leaves[name] = CfnTemplateOutputLeaf(
                    definition=definition,
                )
            except Exception:
                context.log_warning(f"failed to build CfnTemplateOutputLeaf for output [{name}]")


SupportedSourceType = Literal["LocalFilePath", "S3BucketKey", "HttpUrl"]
class CfnTemplateSource:
    type: SupportedSourceType
    source: str
    def __init__(self, source:str, context:AppContext) -> None:
        self.source = source
        if source.startswith("s3://"):
            self.type = "S3BucketKey"
        elif source.startswith("http://") or source.startswith("https://"):
            self.type = "HttpUrl"
        else:
            self.type = "LocalFilePath"

        context.log_debug(f"the type of template source [{self.source}] is [{self.type}]")
    
    @property
    def basename(self) -> str:
        return os.path.basename(self.source)


class CfnTemplateTree:
    """treet CfnTemplate as tree"""
    def __init__(
        self, 
        template_source:CfnTemplateSource,
        definition:CfnTemplateDefinition, 
        spec_repository:ICfnSpecificationRepository,
        context:AppContext,
    ) -> None:
        self.template_source = template_source
        self.description = definition.Description
        self.aws_template_format_version = definition.AWSTemplateFormatVersion
        self.transform = definition.Transform
        self.cfn_docgen_description = definition.get_cfn_docgen_description()

        self.parameters_node = CfnTemplateParametersNode(
            definitions=definition.Parameters,
            parameter_groups=definition.get_parameter_groups(),
            context=context,
        )
        self.mappings_node = CfnTemplateMappingsNode(
            definitions=definition.Mappings,
            descriptions=definition.get_mapping_descriptions(),
            context=context,
        )
        self.rules_node = CfnTemplateRulesNode(
            definitions=definition.Rules,
            descriptions=definition.get_rule_descriptions(),
            context=context,
        )
        self.conditions_node = CfnTemplateConditionsNode(
            definitions=definition.Conditions,
            descriptions=definition.get_condition_descriptions(),
            context=context,
        )
        self.resources_node = CfnTemplateResourcesNode(
            definitions=definition.Resources,
            resource_groups=definition.get_resource_groups(),
            spec_repository=spec_repository,
            context=context,
        )
        self.outputs_node = CfnTemplateOutputsNode(
            definitions=definition.Outputs,
            context=context,
        )

