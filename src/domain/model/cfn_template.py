from __future__ import annotations
import itertools
import json
from jsonpath_ng import jsonpath, parse # type: ignore

from typing import Any, List, Literal, Mapping, Optional, Tuple, TypeAlias, Union, cast, TYPE_CHECKING
from xmlrpc.client import Boolean
from pydantic import BaseModel, Field, PositiveInt
from domain.model.cfn_specification import CfnSpecificationForResource, CfnSpecificationRootProperty, CfnSpecificationChildProperty

from domain.ports.cfn_specification_repository import ICfnSpecificationRepository

from src.domain.model.cfn_template_primitive_type import CfnTemplateResourcePropertyPrimitiveTypeDefinition
CfnTemplateResourcePropertyMapTypeDefinition:TypeAlias = Mapping[Any, Any]
CfnTemplateResourcePropertyListTypeDefinition:TypeAlias = List[Any]
if TYPE_CHECKING:
    # for avoiding circular reference
    from src.domain.model.cfn_template_map_type import CfnTemplateResourcePropertyMapTypeDefinition as m
    from src.domain.model.cfn_template_list_type import CfnTemplateResourcePropertyListTypeDefinition as l
    CfnTemplateResourcePropertyMapTypeDefinition = m # type: ignore
    CfnTemplateResourcePropertyListTypeDefinition = l # type: ignore

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

class CfnTemplateResourceMetadataDefinition(BaseModel):
    CfnDocgen: Optional[CfnTemplateResourceMetadataCfnDocgenDefinition] = None

# CfnTemplateResourcePropertyPrimitiveTypeDefinition:TypeAlias = Union[str,int,float, bool]
# CfnTemplateResourcePropertyListTypeDefinition:TypeAlias = List[
#     Union[
#         'CfnTemplateResourcePropertyPrimitiveTypeDefinition', 
#         'CfnTemplateResourcePropertyMapTypeDefinition',
#         'CfnTemplateResourcePropertyListTypeDefinition',
#     ]
# ]

# CfnTemplateResourcePropertyMapTypeDefinition:TypeAlias = Mapping[
#     str, Union[
#         'CfnTemplateResourcePropertyPrimitiveTypeDefinition',
#         'CfnTemplateResourcePropertyListTypeDefinition',
#         'CfnTemplateResourcePropertyMapTypeDefinition',
#     ]
# ]
CfnTemplateResourcePropertyDefinition = Union[
    'CfnTemplateResourcePropertyPrimitiveTypeDefinition', 
    'CfnTemplateResourcePropertyMapTypeDefinition', 
    'CfnTemplateResourcePropertyListTypeDefinition'
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


    def get_description_for_property(self, json_path:str) -> Optional[str]:
        metadata = self.Metadata
        if metadata is None:
            return None
        cfn_docgen = metadata.CfnDocgen
        if cfn_docgen is None:
            return None
        properties = cfn_docgen.Properties
        if properties is None:
            return None

        descriptions:List[str] = []
        jsonpath_expr = parse(json_path) # type: ignore
        descriptions = [f.value for f in jsonpath_expr.find(properties)] # type: ignore
        if len(descriptions) != 1:
            return None
        return descriptions[0]

    def get_definition_for_property(self, json_path:str) -> Optional[CfnTemplateResourcePropertyDefinition]:
        definitions:List[CfnTemplateResourcePropertyDefinition] = []
        jsonpath_expr = parse(json_path) # type: ignore
        definitions = [f.value for f in jsonpath_expr.find(self.Properties)] # type: ignore
        if len(definitions) != 1:
            return None
        return definitions[0]
    
CfnTemplateResourceDefinition.model_rebuild()

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


class CfnTemplateParametersNode:

    group_name_for_independent_parameters = "__CFN_DOCGEN_INDEPENDENT_PARAMETERS__"

    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateParameterDefinition],
        parameter_groups:List[CfnTemplateMetadataParameterGroup]
    ) -> None:
        
        self.group_nodes:Mapping[str, CfnTemplateParameterGroupNode] = {
            group.Label.default: CfnTemplateParameterGroupNode(
                definitions={
                    param_name: definition 
                    for param_name, definition in definitions.items()
                    if param_name in group.Parameters
                }
            )
            for group in parameter_groups
        }

        parameter_names_in_groups = list(itertools.chain.from_iterable(
            [group.Parameters for group in parameter_groups]
        ))
        self.group_nodes[self.group_name_for_independent_parameters] = CfnTemplateParameterGroupNode(
            definitions={
                param_name: definition for param_name, definition in definitions.items()
                if param_name not in parameter_names_in_groups
            }
        )


class CfnTemplateParameterGroupNode:

    def __init__(
        self,
        definitions:Mapping[str, CfnTemplateParameterDefinition],
    ) -> None:
        self.leaves = {name: CfnTemplateParameterLeaf(definition) for name, definition in definitions.items()}
        

class CfnTemplateParameterLeaf:
    def __init__(self, definition:CfnTemplateParameterDefinition) -> None:
        self.definition = definition
        

# class CfnTemplateMapping:

#     def __init__(self, name:str, definition:Mapping[str, Mapping[str, Any]], metadata:CfnTemplateMetadataDefinition|None) -> None:
#         self.name = name
#         self.definition = definition

#         self.description = self.get_description(name, metadata)

#     def get_description(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
#         if metadata is None:
#             return
#         cfn_docgen = metadata.CfnDocgen
#         if cfn_docgen is None:
#             return
#         return cfn_docgen.Mappings.get(name, None)

# class CfnTemplateCondition:

#     def __init__(self, name:str, definition:Mapping[str, Any], metadata:CfnTemplateMetadataDefinition|None) -> None:
#         self.name = name
#         self.definition = definition

#         self.description = self.get_description(name, metadata)
    
#     def get_description(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
#         if metadata is None:
#             return
#         cfn_docgen = metadata.CfnDocgen
#         if cfn_docgen is None:
#             return
#         return cfn_docgen.Conditions.get(name, None)

# class CfnTemplateRule:

#     def __init__(self, name:str, definition:CfnTemplateRuleDefinition, metadata:CfnTemplateMetadataDefinition|None) -> None:
#         self.name = name
#         self.definition = definition

#         self.description = self.get_description(name, metadata)
        
#     def get_description(self, name:str, metadata:CfnTemplateMetadataDefinition|None) -> Optional[str]:
#         if metadata is None:
#             return
#         cfn_docgen = metadata.CfnDocgen
#         if cfn_docgen is None:
#             return
#         return cfn_docgen.Rules.get(name, None)

# class CfnTemplateResourceChildProperty:
#     def __init__(
#         self,
#         prop_name:str, 
#         prop_type:str,
#         resource_definition:CfnTemplateResourceDefinition, 
#         specs:CfnSpecificationForResource,
#         parent_path:str,
#         index:Optional[int], depth:int,
#     ) -> None:
#         self.name = prop_name
#         self.type = prop_type
#         self.index = index
#         self.depth = depth
#         self.json_path = self.append_json_path(
#             name=prop_name, parent_path=parent_path, index=index
#         )

#         self.description = resource_definition.get_description_for_property(self.json_path)
#         self.definition = resource_definition.get_definition_for_property(self.json_path)
#         self.property_spec:CfnSpecificationRootProperty|None = None
#         self.primitive_spec:CfnSpecificationChildProperty|None = None

#         self.property_spec = specs.PropertySpecs.get(f"{resource_definition.Type}.{prop_type}")
#         if self.property_spec is not None and self.property_spec.Properties is not None:
#             self.primitive_spec = self.property_spec.Properties.get(prop_name, None)

#         self.properties:List[CfnTemplateResourceChildProperty] = []

#         if self.primitive_spec is not None:
#             if (
#                 self.primitive_spec.PrimitiveType is not None
#                 or self.primitive_spec.PrimitiveItemType is not None
#             ):
#                 return
        
#         # if self.property_spec is None:
#         #     return
#         # if self.spec.PrimitiveType is not None:
#         #     return        
#         # if self.spec.PrimitiveItemType is not None:
#         #     return
#         # if self.spec.Type is None:
#         #     return

#         if self.property_spec is None or self.property_spec.Properties is None:
#             return
#         for child_prop_name, child_prop_body in self.property_spec.Properties.items():
#             if child_prop_body.Type is None:
#                 self.properties.append(
#                     CfnTemplateResourceChildProperty(
#                         prop_name=child_prop_name,
#                         prop_type=self.type,
#                         resource_definition=resource_definition,
#                         specs=specs,
#                         parent_path=self.json_path,
#                         index=None, depth=self.depth+1
#                     )
#                 )
#                 continue
#             match child_prop_body.Type.lower():
#                 case "list":
#                     definition_len = len(
#                         cast(List[Any] ,self.definition) 
#                         if self.definition is not None else []
#                     )
#                     for i in range(max(1, definition_len)):
#                         self.properties.append(
#                             CfnTemplateResourceChildProperty(
#                                 prop_name=child_prop_name,
#                                 prop_type=self.type,
#                                 resource_definition=resource_definition,
#                                 specs=specs,
#                                 parent_path=self.json_path,
#                                 index=i, depth=self.depth+1
#                             )
#                         )
#                     continue
#                 case "map":
#                     definition_map = cast(Mapping[Any, Any], self.definition) if self.definition is not None else {"Key": None}
#                     for key in definition_map.keys():
#                         self.properties.append(
#                             CfnTemplateResourceChildProperty(
#                                 prop_name=f"{child_prop_name}.{key}",
#                                 prop_type=self.type,
#                                 resource_definition=resource_definition,
#                                 specs=specs,
#                                 parent_path=self.json_path,
#                                 index=None, depth=self.depth+1
#                             )
#                         )
#                     continue
#                 case _:
#                     self.properties.append(
#                         CfnTemplateResourceChildProperty(
#                             prop_name=child_prop_name,
#                             prop_type=self.type,
#                             resource_definition=resource_definition,
#                             specs=specs,
#                             parent_path=self.json_path,
#                             index=None, depth=self.depth+1
#                         )
#                     )
#                     continue

#     def append_json_path(self, name:str, parent_path:str, index:int|None) -> str:
#         path = parent_path
#         if index is not None:
#             path += f"[{index}]"
#         path += f".{name}"
#         return path


# class CfnTemplateResourceRootProperty:

#     def __init__(
#         self, 
#         prop_name:str,
#         prop_type:str, 
#         resource_definition:CfnTemplateResourceDefinition, 
#         specs:CfnSpecificationForResource,
#         parent_path:str,
#         index:Optional[int], depth:int,
#     ) -> None:
        
#         self.name = prop_name
#         self.type = prop_type
#         self.index = index
#         self.depth = depth
#         self.json_path = self.append_json_path(
#             name=prop_name, parent_path=parent_path, index=index,
#         )

#         self.description = resource_definition.get_description_for_property(self.json_path)
#         self.definition = resource_definition.get_definition_for_property(self.json_path)
#         self.spec = specs.ResourceSpec.Properties[prop_type]

#         self.properties:Optional[List[CfnTemplateResourceChildProperty]] = []
#         if self.spec.PrimitiveType is not None:
#             return        
#         if self.spec.PrimitiveItemType is not None:
#             return
        
#         if self.spec.Type is None:
#             return
        

#         child_spec = specs.PropertySpecs.get(f"{resource_definition.Type}.{self.spec.Type}", None)
#         if child_spec is None or child_spec.Properties is None:
#             return
#         for child_prop_name in child_spec.Properties.keys():
#             match self.spec.Type.lower():
#                 case "list":
#                     definition_len = len(
#                         cast('CfnTemplateResourcePropertyListTypeDefinition',self.definition) 
#                         if self.definition is not None else []
#                     )
#                     for i in range(max(1, definition_len)):
#                         self.properties.append(
#                             CfnTemplateResourceChildProperty(
#                                 prop_name=child_prop_name,
#                                 prop_type=child_prop_name,
#                                 resource_definition=resource_definition,
#                                 specs=specs,
#                                 parent_path=self.json_path,
#                                 index=i, depth=self.depth+1
#                             )
#                         )
#                     continue
#                 case "map":
#                     definition_map = cast('CfnTemplateResourcePropertyMapTypeDefinition', self.definition) if self.definition is not None else {"Key": None}
#                     for key in definition_map.keys():
#                         self.properties.append(
#                             CfnTemplateResourceChildProperty(
#                                 prop_name=f"{child_prop_name}.{key}",
#                                 prop_type=child_prop_name,
#                                 resource_definition=resource_definition,
#                                 specs=specs,
#                                 parent_path=self.json_path,
#                                 index=None, depth=self.depth+1
#                             )
#                         )
#                     continue
#                 case _:
#                     self.properties.append(
#                         CfnTemplateResourceChildProperty(
#                             prop_name=child_prop_name,
#                             prop_type=child_prop_name,
#                             resource_definition=resource_definition,
#                             specs=specs,
#                             parent_path=self.json_path,
#                             index=None, depth=self.depth+1
#                         )
#                     )
#                     continue

                    
#     def append_json_path(self, name:str, parent_path:str, index:int|None) -> str:
#         path = parent_path
#         if index is not None:
#             path += f"[{index}]"
#         path += f".{name}"
#         return path

#     # def determine_type_representation(self, ) -> str:
#     #     if self.spec.PrimitiveType is not None:
#     #         return self.spec.PrimitiveType
#     #     if self.spec.PrimitiveItemType is not None and self.spec.Type is not None:
#     #         return f"{self.spec.Type} of {self.spec.PrimitiveItemType}"
#     #     if self.spec.ItemType is not None and self.spec.Type is not None:
#     #         return f"{self.spec.Type} of {self.spec.ItemType}"
#     #     if self.spec.Type is not None:
#     #         return self.spec.Type
        
#     #     return "N/A"


# class CfnTemplateResource:

#     def __init__(self, name:str, definition:CfnTemplateResourceDefinition, specs:CfnSpecificationForResource) -> None:
#         self.name = name
#         self.definition = definition
#         self.description = self.get_description(definition)
#         self.spec = specs.ResourceSpec

#         self.properties:List[CfnTemplateResourceRootProperty] = []
#         self.properties = [
#             CfnTemplateResourceRootProperty(
#                 prop_name=name, 
#                 prop_type=name,
#                 resource_definition=definition,
#                 specs=specs,
#                 parent_path="$",
#                 index=None, depth=0,
#             ) for name in specs.PropertySpecs.keys()
#         ]

#     def get_description(self, definition:CfnTemplateResourceDefinition) -> Optional[str]:
#         metadata = definition.Metadata
#         if metadata is None:
#             return
#         cfn_docgen = metadata.CfnDocgen
#         if cfn_docgen is None:
#             return
#         return cfn_docgen.Description

# class CfnTemplateOutput:

#     def __init__(self, name:str, definition:CfnTemplateOutputDefinition) -> None:
#         self.name = name
#         self.definition = definition

# class CfnTemplateTree:
#     """treet CfnTemplate as tree"""
#     def __init__(self, 
#         definition:CfnTemplateDefinition, 
#         spec_repository:ICfnSpecificationRepository,
#     ) -> None:
        
#         self.definition = definition
#         self.parameter_nodes = CfnTemplateParametersNode(definition.Parameters)


# class CfnTemplate:
#     def __init__(self, filepath:str, definition:CfnTemplateDefinition, spec_repository:ICfnSpecificationRepository) -> None:
#         self.filepath = filepath
#         self.definition = definition
#         self.parameters = [
#             CfnTemplateParameter(name, definition.Parameters[name], definition.Metadata) for name in definition.Parameters.keys()
#         ]
#         self.mappings = [
#             CfnTemplateMapping(name, definition.Mappings[name], definition.Metadata) for name in definition.Mappings.keys()
#         ]
#         self.conditions = [
#             CfnTemplateCondition(name, definition.Conditions[name], definition.Metadata) for name in definition.Conditions.keys()
#         ]
#         self.rules = [
#             CfnTemplateRule(name, definition.Rules[name], definition.Metadata) for name in definition.Rules.keys()
#         ]
#         self.resources = [
#             CfnTemplateResource(
#                 name, definition, 
#                 spec_repository.get_specs_for_resource(definition.Type)
#             ) for name, definition in definition.Resources.items()
#         ]
#         self.outputs = [
#             CfnTemplateOutput(name, definition.Outputs[name]) for name in definition.Outputs.keys()
#         ]

#     def get_parameters_by_group(self, ) -> Tuple[Mapping[str, List[CfnTemplateParameter]], List[CfnTemplateParameter]]:
#         parameters_by_group:Mapping[str, List[CfnTemplateParameter]] = {}
#         ungrouped_parameters:List[CfnTemplateParameter] = []
#         for parameter in self.parameters:
#             group = parameter.group
#             if group is None:
#                 ungrouped_parameters.append(parameter)
#                 continue
#             if parameters_by_group.get(group, None) is None:
#                 parameters_by_group[group] = [parameter]
#             else:
#                 parameters_by_group[group].append(parameter)
        
#         return parameters_by_group, ungrouped_parameters

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
