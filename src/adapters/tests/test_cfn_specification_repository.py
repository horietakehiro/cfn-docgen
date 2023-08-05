import pytest
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.internal.cache import NoFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig


@pytest.fixture
def cfn_specification_url():
    return "https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"

def test_CfnSpecificationRepository_get_resource_spec(cfn_specification_url:str):
    repository = CfnSpecificationRepository(
        loader=RemoteFileLoader(cfn_specification_url),
        cache=NoFileCache(AppConfig()),
    )

    for resource_type in repository.spec.ResourceTypes.keys():
        resource_spec = repository.get_resource_spec(resource_type)
        assert resource_spec is not None
        if resource_spec.Documentation is not None:
            assert (
                resource_spec.Documentation.startswith("http://") or resource_spec.Documentation.startswith("https://")
            ) , f"{resource_type}/{resource_spec.Documentation}"
        
        for prop_name, prop in resource_spec.Properties.items():
            if prop.Documentation is not None:
                assert (
                    prop.Documentation.startswith("http://") or prop.Documentation.startswith("https://")
                ), f"{resource_type}/{prop_name}/{prop.Documentation}/"

            if prop.PrimitiveItemType is not None or prop.ItemType is not None:
                assert prop.Type is not None and (prop.Type == "List" or prop.Type == "Map"), f"{resource_type}/{prop_name}/{prop}"
            if prop.Type is not None and (prop.Type != "List" and prop.Type != "Map"):
                assert (
                    prop.PrimitiveItemType is None and prop.ItemType is None and prop.PrimitiveType is None
                ), f"{resource_type}/{prop_name}/{prop}"

def test_CfnSpecificationRepository_get_property_spec(cfn_specification_url:str):
    repository = CfnSpecificationRepository(
        loader=RemoteFileLoader(cfn_specification_url),
        cache=NoFileCache(AppConfig()),
    )
    for property_type in repository.spec.PropertyTypes.keys():
        property_spec = repository.get_property_spec(property_type)
        assert property_spec is not None
        if property_spec.Documentation is not None:
            assert (
                property_spec.Documentation.startswith("http://") or property_spec.Documentation.startswith("https://")
            ), f"{property_type}/{property_spec.Documentation}"

        if property_spec.Properties is None:
            assert (
                property_spec.ItemType is not None or
                property_spec.PrimitiveItemType is not None or
                property_spec.PrimitiveType is not None or
                property_spec.Type is not None
            ) , f"{property_type}/{property_spec}"
        
        else:
            for prop_name, prop in property_spec.Properties.items():
                with open("./tmp.csv", "a") as fp:
                    fp.write(f"{prop.Type},{prop.ItemType},{prop.PrimitiveItemType},{prop.PrimitiveType}\n")
                if prop.Documentation is not None:
                    assert (
                        prop.Documentation.startswith("http://") or prop.Documentation.startswith("https://")
                    ), f"{property_type}/{prop_name}/{prop.Documentation}/"

                if prop.PrimitiveItemType is not None or prop.ItemType is not None:
                    assert prop.Type is not None and (prop.Type == "List" or prop.Type == "Map"), f"{property_type}/{prop_name}/{prop}"
                if prop.Type is not None and (prop.Type != "List" and prop.Type != "Map"):
                    assert (
                        prop.PrimitiveItemType is None and prop.ItemType is None and prop.PrimitiveType is None
                    ), f"{property_type}/{prop_name}/{prop}"

    raise NotImplementedError