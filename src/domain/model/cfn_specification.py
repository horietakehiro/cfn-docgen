from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Literal, Mapping, Optional
from pydantic import BaseModel

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


# class CfnSpecificationChildProperty(BaseModel):
#     Documentation: Optional[str] = None
#     DuplicatesAllowed: Optional[bool] = None
#     ItemType: Optional[str] = None
#     PrimitiveType: Optional[str] = None
#     PrimitiveItemType: Optional[str] = None
#     Required: Optional[bool] = None
#     Type: Optional[str] = None
#     UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None


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


class CfnSpecificationResourceTypeName:
    fullname:str
    __pattern = r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$"

    def __init__(self, resource_type:str) -> None:
        assert re.match(self.__pattern, resource_type) is not None, f"Valid pattern for PropertyType is {self.__pattern} (e.g. AWS::EC2::Instance)"
        self.fullname = resource_type

    # def __hash__(self) -> int:
    #     return hash(self.fullname)
    
    # def __eq__(self, __value: object) -> bool:
    #     return isinstance(__value, CfnSpecificationResourceType) and self.fullname == __value.fullname

class CfnSpecificationPropertyTypeName:
    fullname:str
    __pattern = r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+\.[a-zA-Z0-9]+$|^Tag$"

    def __init__(self, property_type:str) -> None:
        assert re.match(self.__pattern, property_type) is not None, f"Valid pattern for PropertyType is {self.__pattern} (e.g. AWS::EC2::Instance.BlockDeviceMapping)"
        self.fullname = property_type

    @property
    def prefix(self, ) -> str:
        return self.fullname.split(".")[0]
    
    @property
    def suffix(self, ) -> str:
        return self.fullname.split(".")[-1]
    
    # def __hash__(self) -> int:
    #     return hash(self.fullname)
    
    # def __eq__(self, __value: object) -> bool:
    #     return isinstance(__value, CfnSpecificationPropertyType) and self.fullname == __value.fullname
