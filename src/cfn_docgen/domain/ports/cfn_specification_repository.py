from abc import ABC, abstractmethod
from typing import List, Mapping
from cfn_docgen.config import AppContext
from cfn_docgen.domain.ports.cache import IFileCache
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

from cfn_docgen.domain.model.cfn_specification import CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName, CfnSpecificationPropertyType, CfnSpecificationResourceType, CfnSpecificationForResource


class ICfnSpecificationRepository(ABC):

    def __init__(
        self,
        source_url:str,
        loader:IFileLoader, 
        cache:IFileCache, 
        recursive_resource_types:List[str],
        context:AppContext,
    ) -> None:
        self.context = context
        self.recursive_resource_types = recursive_resource_types
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

    @abstractmethod
    def is_recursive(self, resource_type:CfnSpecificationResourceTypeName) -> bool:
        pass

