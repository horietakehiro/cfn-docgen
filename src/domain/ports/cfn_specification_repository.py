from abc import ABC, abstractmethod
from typing import Mapping, Optional
from domain.ports.cache import IFileCache
from domain.ports.file_loader import IFileLoader

from src.domain.model.cfn_specification import CfnSpecificationRootProperty, CfnSpecificationResource, CfnSpecificationForResource


class ICfnSpecificationRepository(ABC):

    def __init__(self, loader:IFileLoader, cache:IFileCache) -> None:
        super().__init__()

    @abstractmethod
    def get_resource_spec(self, resource_type:str) -> CfnSpecificationResource:
        pass

    @abstractmethod
    def get_property_spec(self, property_type:str) -> CfnSpecificationRootProperty:
        pass


    @abstractmethod
    def list_properties_for_resource(self, resource_type:str) -> Mapping[str, CfnSpecificationRootProperty]:
        pass


    @abstractmethod
    def get_specs_for_resource(self, resource_type:str) -> CfnSpecificationForResource:
        pass
