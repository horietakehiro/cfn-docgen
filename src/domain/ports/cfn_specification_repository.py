from abc import ABC, abstractmethod
from typing import Mapping
from domain.ports.cache import IFileCache
from domain.ports.file_loader import IFileLoader

from src.domain.model.cfn_specification import CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName, CfnSpecificationPropertyType, CfnSpecificationResourceType, CfnSpecificationForResource


class ICfnSpecificationRepository(ABC):

    def __init__(self, loader:IFileLoader, cache:IFileCache) -> None:
        super().__init__()

    @abstractmethod
    def get_resource_spec(self, resource_type:CfnSpecificationResourceTypeName) -> CfnSpecificationResourceType:
        pass

    @abstractmethod
    def get_property_spec(self, property_type:CfnSpecificationPropertyTypeName) -> CfnSpecificationPropertyType:
        pass


    @abstractmethod
    def list_properties_for_resource(self, resource_type:CfnSpecificationResourceTypeName) -> Mapping[str, CfnSpecificationPropertyType]:
        pass


    @abstractmethod
    def get_specs_for_resource(self, resource_type:CfnSpecificationResourceTypeName) -> CfnSpecificationForResource:
        pass
