
import json
from typing import Mapping
from domain.model.cfn_specification import CfnSpecificationForResource, CfnSpecificationPropertyType, CfnSpecificationResourceType
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

    def get_resource_spec(self, resource_type: str) -> CfnSpecificationResourceType:
        try:
            return self.spec.ResourceTypes[resource_type]
        except KeyError as ex:
            raise ex

    def get_property_spec(self, property_type: str) -> CfnSpecificationPropertyType:
        try:
            return self.spec.PropertyTypes[property_type]
        except KeyError as ex:
            raise ex

    def list_properties_for_resource(self, resource_type: str) -> Mapping[str, CfnSpecificationPropertyType]:
        property_specs:Mapping[str, CfnSpecificationPropertyType] = {}
        for property_type, property_spec in self.spec.PropertyTypes.items():
            if property_type.startswith(f"{resource_type}.") or property_type == "Tag":
                property_specs[property_type] = property_spec
        return property_specs


    def get_specs_for_resource(self, resource_type: str) -> CfnSpecificationForResource:
        resource_spec = self.get_resource_spec(resource_type)
        property_specs = self.list_properties_for_resource(resource_type)
        return CfnSpecificationForResource(
            ResourceSpec=resource_spec,
            PropertySpecs=property_specs,
        )
