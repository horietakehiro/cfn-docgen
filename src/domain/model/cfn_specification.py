from dataclasses import dataclass
from typing import Literal, Mapping, Optional
from pydantic import BaseModel

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

class CfnSpecificationResourceType(BaseModel):
    AdditionalProperties: Optional[bool] = None
    Attributes: Mapping[str, CfnSpecificationResourceTypeAttribute] = {}
    Documentation: Optional[str] = None
    Properties: Mapping[str, CfnSpecificationResourceTypeProperty] = {}


class CfnSpecificationPropertyTypeProperty(BaseModel):
    Documentation: Optional[str] = None
    DuplicatesAllowed: Optional[bool] = None
    ItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    Required: Optional[bool] = None
    Type: Optional[str] = None
    UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None


class CfnSpecificationPropertyType(BaseModel):
    Documentation: Optional[str] = None
    DuplicatesAllowed: Optional[bool] = None
    ItemType: Optional[str] = None
    PrimitiveType: Optional[str] = None
    PrimitiveItemType: Optional[str] = None
    Required: Optional[bool] = None
    Type: Optional[str] = None
    UpdateType: Optional[Literal["Conditional", "Immutable", "Mutable"]] = None
    Properties: Optional[Mapping[str, CfnSpecificationPropertyTypeProperty]] = None

@dataclass
class CfnSpecificationForResource:
    ResourceSpec: CfnSpecificationResourceType
    PropertySpecs: Mapping[str, CfnSpecificationPropertyType]

class CfnSpecification(BaseModel):
    ResourceSpecificationVersion: str
    ResourceTypes: Mapping[str, CfnSpecificationResourceType]
    PropertyTypes: Mapping[str, CfnSpecificationPropertyType]