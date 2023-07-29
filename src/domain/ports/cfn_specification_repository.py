from abc import ABC, abstractmethod


class ICfnSpecificationRepository(ABC):

    def __init__(self, ) -> None:
        super().__init__()

    @abstractmethod
    def get_resource_spec(self, resource_type:str):
        pass

    @abstractmethod
    def get_property_spec(self, resource_type:str, property_name:str):
        pass