from abc import ABC, abstractmethod
from typing import Optional
from domain.ports.cache import IFileCache
from domain.ports.file_loader import IFileLoader

from src.domain.model.cfn_specification import CfnSpecificationPropertyType, CfnSpecificationResourceType


class ICfnSpecificationRepository(ABC):

    def __init__(self, loader:IFileLoader, cache:IFileCache) -> None:
        super().__init__()

    @abstractmethod
    def get_resource_spec(self, resource_type:str) -> Optional[CfnSpecificationResourceType]:
        pass

    @abstractmethod
    def get_property_spec(self, property_type:str) -> Optional[CfnSpecificationPropertyType]:
        pass
