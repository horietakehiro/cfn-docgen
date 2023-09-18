from abc import ABC, abstractmethod
from typing import Callable, List, Mapping, Optional
from cfn_docgen.config import AppContext
from cfn_docgen.domain.ports.cache import IFileCache
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

from cfn_docgen.domain.model.cfn_specification import CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName, CfnSpecificationPropertyType, CfnSpecificationResourceType, CfnSpecificationForResource


class ICfnSpecificationRepository(ABC):

    @abstractmethod
    def __init__(
        self,
        source_url:str,
        loader_factory:Callable[[str, AppContext], IFileLoader], 
        cache:IFileCache, 
        recursive_resource_types:List[str],
        context:AppContext,
        custom_resource_specification_url:Optional[str]=None,
    ) -> None:
        pass

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

    @abstractmethod
    def list_resource_types(self, ) -> List[str]:
        pass