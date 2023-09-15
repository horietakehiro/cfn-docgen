from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Mapping, Literal, Optional
from pydantic import BaseModel

from cfn_docgen.config import AppContext


class CfnSpecificationProperty(BaseModel):
    Documentation: Optional[str] = None
    DuplicatesAllowed: Optional[bool] = None
    ItemType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    Required: Optional[bool] = None
    Type: Optional[str] = None
    UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None

class CfnSpecificationResourceTypeAttribute(BaseModel):
    ItemType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    Type: Optional[str] = None

class CfnSpecificationResourceType(BaseModel):
    AdditionalProperties: Optional[bool] = None
    Attributes: Mapping[str, CfnSpecificationResourceTypeAttribute] = {}
    Documentation: Optional[str] = None
    Properties: Mapping[str, CfnSpecificationProperty] = {}


class CfnSpecificationPropertyType(BaseModel):
    Documentation: Optional[str] = None
    DuplicatesAllowed: Optional[bool] = None
    ItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    Required: Optional[bool] = None
    Type: Optional[str] = None
    UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None
    Properties: Optional[Mapping[str, CfnSpecificationProperty]] = None


@dataclass
class CfnSpecificationForResource:
    ResourceSpec: CfnSpecificationResourceType
    PropertySpecs: Mapping[str, CfnSpecificationPropertyType]

class CfnSpecification(BaseModel):
    ResourceSpecificationVersion: str
    ResourceTypes: Mapping[str, CfnSpecificationResourceType]
    PropertyTypes: Mapping[str, CfnSpecificationPropertyType]

    def merge_with_custom_specification(
        self,
        custom_specification:CfnSpecification,
        context:AppContext,
    ) -> None:
        for resource_type, resource_spec in custom_specification.ResourceTypes.items():
            if self.ResourceTypes.get(resource_type, None):
                context.log_debug(f"overwrite resource type [{resource_type}] with custom one")
            else:
                context.log_debug(f"add custom resource type [{resource_type}]")
            self.ResourceTypes[resource_type] = resource_spec # type: ignore

        for property_type, property_spec in custom_specification.PropertyTypes.items():
            if self.PropertyTypes.get(property_type, None):
                context.log_debug(f"overwrite property type [{property_type}] with custom one")
            else:
                context.log_debug(f"add custom property type [{property_type}]")
            self.PropertyTypes[property_type] = property_spec # type: ignore

class CfnSpecificationResourceTypeName:
    fullname:str
    __pattern = r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$|^Custom::[a-zA-Z0-9]+$"

    def __init__(self, resource_type:str, context:AppContext) -> None:
        try:
            assert re.match(self.__pattern, resource_type) is not None, f"Valid pattern for ResourceType is {self.__pattern} (e.g. AWS::EC2::Instance)"
        except AssertionError as ex:
            context.log_error(f"failed to instanciate for resource type {resource_type}. {str(ex)}")
            raise ex

        self.fullname = resource_type

class CfnSpecificationPropertyTypeName:
    fullname:str
    __pattern = r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+\.[a-zA-Z0-9]+$|^Tag$|^Custom::[a-zA-Z0-9]+\.[a-zA-Z0-9]+$"

    def __init__(self, property_type:str, context:AppContext) -> None:
        try:
            assert re.match(self.__pattern, property_type) is not None, f"Valid pattern for PropertyType is {self.__pattern} (e.g. AWS::EC2::Instance.BlockDeviceMapping)"
        except AssertionError as ex:
            context.log_error(f"failed to instanciate for property type {property_type}. {str(ex)}")
            raise ex
        self.fullname = property_type

    @property
    def prefix(self, ) -> str:
        return self.fullname.split(".")[0]
    
    @property
    def suffix(self, ) -> str:
        return self.fullname.split(".")[-1]