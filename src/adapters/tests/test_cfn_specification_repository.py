import pytest
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig


@pytest.fixture
def cfn_specification_url():
    return "https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"

@pytest.fixture
def repository():
    return CfnSpecificationRepository(
        loader=RemoteFileLoader("https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"),
        cache=LocalFileCache(AppConfig()),
    )

def test_CfnSpecificationRepository_get_resource_spec(repository:CfnSpecificationRepository):

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

def test_CfnSpecificationRepository_get_resource_spec_KeyError(repository:CfnSpecificationRepository):
    invalid_key = "AWS::Invalid::Key"
    with pytest.raises(KeyError) as ex:
        repository.get_resource_spec(invalid_key)
    assert invalid_key in ex.value.args 

def test_CfnSpecificationRepository_get_property_spec_KeyError(repository:CfnSpecificationRepository):
    invalid_key = "AWS::Invalid::Key.1"
    with pytest.raises(KeyError) as ex:
        repository.get_property_spec(invalid_key)
    assert invalid_key in ex.value.args 


def test_CfnSpecificationRepository_get_property_spec(repository:CfnSpecificationRepository):
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

def test_CfnSpecificationRepository_list_properties_for_resource(repository:CfnSpecificationRepository):
    resource_type = "AWS::EC2::Instance"
    proeprties = repository.list_properties_for_resource(resource_type)
    assert proeprties.get(f"{resource_type}.BlockDeviceMapping")
    assert proeprties.get(f"{resource_type}.Ebs")


def test_CfnSpecificationRepository_get_specs_for_resources(repository:CfnSpecificationRepository):
    resource_type = "AWS::EC2::Instance"
    specs = repository.get_specs_for_resource(resource_type)
    assert specs.PropertySpecs.get(f"{resource_type}.BlockDeviceMapping")
    assert specs.PropertySpecs.get(f"{resource_type}.Ebs")

