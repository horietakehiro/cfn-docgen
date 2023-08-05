import json
from domain.model.cfn_specification import CfnSpecificationPropertyType, CfnSpecificationResourceType
from src.domain.model.cfn_specification import CfnSpecification
from src.domain.ports.cache import IFileCache
from src.domain.ports.file_loader import IFileLoader
from src.domain.ports.cfn_specification_repository import ICfnSpecificationRepository


class CfnSpecificationRepository(ICfnSpecificationRepository):
    def __init__(self, loader: IFileLoader, cache: IFileCache) -> None:
        cached = cache.get(loader.filepath)
        if cached is None:
            json_str = loader.load()
            self.spec = CfnSpecification(**json.loads(json_str))
            cache.put(loader.filepath, json_str)
        else:
            self.spec = CfnSpecification(**json.loads(cached))

    def get_resource_spec(self, resource_type: str) -> CfnSpecificationResourceType | None:
        return self.spec.ResourceTypes.get(resource_type, None)

    def get_property_spec(self, property_type: str) -> CfnSpecificationPropertyType | None:
        return self.spec.PropertyTypes.get(property_type, None)
