from dataclasses import dataclass, field
import re
from typing import Literal, Mapping, Optional
from pydantic import BaseModel, Field, PositiveInt, constr

class CfnSpecificationResourceTypeProperty(BaseModel):
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

class CfnSpecificationResource(BaseModel):
    AdditionalProperties: Optional[bool] = None
    Attributes: Mapping[str, CfnSpecificationResourceTypeAttribute] = {}
    Documentation: Optional[str] = None
    Properties: Mapping[str, CfnSpecificationResourceTypeProperty] = {}


class CfnSpecificationChildProperty(BaseModel):
    Documentation: Optional[str] = None
    DuplicatesAllowed: Optional[bool] = None
    ItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    Required: Optional[bool] = None
    Type: Optional[str] = None
    UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None


class CfnSpecificationRootProperty(BaseModel):
    Documentation: Optional[str] = None
    DuplicatesAllowed: Optional[bool] = None
    ItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    Required: Optional[bool] = None
    Type: Optional[str] = None
    UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None
    Properties: Optional[Mapping[str, CfnSpecificationChildProperty]] = None

@dataclass
class CfnSpecificationForResource:
    ResourceSpec: CfnSpecificationResource
    PropertySpecs: Mapping[str, CfnSpecificationRootProperty]

class CfnSpecification(BaseModel):
    ResourceSpecificationVersion: str
    ResourceTypes: Mapping[str, CfnSpecificationResource]
    PropertyTypes: Mapping[str, CfnSpecificationRootProperty]


class CfnSpecificationResourceType:
    fullname:str
    __pattern = r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$"

    def __init__(self, resource_type:str) -> None:
        assert re.match(self.__pattern, resource_type) is not None, f"Valid pattern for PropertyType is {self.__pattern} (e.g. AWS::EC2::Instance)"
        self.fullname = resource_type

class CfnSpecificationPropertyType:
    fullname:str
    __pattern = r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+\.[a-zA-Z0-9]+$"

    def __init__(self, property_type:str) -> None:
        assert re.match(self.__pattern, property_type) is not None, f"Valid pattern for PropertyType is {self.__pattern} (e.g. AWS::EC2::Instance.BlockDeviceMapping)"
        self.fullname = property_type

    @property
    def prefix(self, ) -> str:
        return self.fullname.split(".")[0]
    
    @property
    def suffix(self, ) -> str:
        return self.fullname.split(".")[1]
        