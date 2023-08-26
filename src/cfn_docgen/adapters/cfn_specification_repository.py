import json
from typing import List, Mapping

from cfn_docgen.domain.model.cfn_specification import CfnSpecificationForResource, CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName, CfnSpecificationPropertyType, CfnSpecificationResourceType
from cfn_docgen.domain.model.cfn_specification import CfnSpecification
from cfn_docgen.domain.ports.cache import IFileCache
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader
from cfn_docgen.domain.ports.cfn_specification_repository import ICfnSpecificationRepository


class CfnSpecificationRepository(ICfnSpecificationRepository):
    def __init__(
        self, 
        source_url:str,
        loader: IFileLoader, 
        cache: IFileCache, 
        recursive_resource_types:List[str]
    ) -> None:
        cached = cache.get(source_url)
        if cached is None:
            json_bytes = loader.download(source_url)
            json_str = json_bytes.decode()
            self.spec = CfnSpecification(**json.loads(json_str))
            cache.put(source_url, json_str)
        else:
            self.spec = CfnSpecification(**json.loads(cached))

        self.recursive_resource_types = recursive_resource_types

    def get_resource_spec(self, resource_type: CfnSpecificationResourceTypeName) -> CfnSpecificationResourceType:
        try:
            return self.spec.ResourceTypes[resource_type.fullname]
        except KeyError as ex:
            raise ex

    def get_property_spec(self, property_type: CfnSpecificationPropertyTypeName) -> CfnSpecificationPropertyType:
        try:
            return self.spec.PropertyTypes[property_type.fullname]
        except KeyError as ex:
            raise ex

    def list_properties_for_resource(self, resource_type: CfnSpecificationResourceTypeName) -> Mapping[str, CfnSpecificationPropertyType]:
        property_specs:Mapping[str, CfnSpecificationPropertyType] = {}
        for property_type, property_spec in self.spec.PropertyTypes.items():
            if property_type.startswith(f"{resource_type.fullname}.") or property_type == "Tag":
                property_specs[property_type] = property_spec
        return property_specs


    def get_specs_for_resource(self, resource_type: CfnSpecificationResourceTypeName) -> CfnSpecificationForResource:
        resource_spec = self.get_resource_spec(resource_type)
        property_specs = self.list_properties_for_resource(resource_type)
        return CfnSpecificationForResource(
            ResourceSpec=resource_spec,
            PropertySpecs=property_specs,
        )

    def is_recursive(self, resource_type: CfnSpecificationResourceTypeName) -> bool:
        return super().is_recursive(resource_type)