import pytest
from adapters.cfn_specification_repository import CfnSpecificationRepository
from adapters.internal.cache import LocalFileCache
from adapters.internal.file_loader import RemoteFileLoader
from config import AppConfig
from domain.model.cfn_specification import CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName


@pytest.fixture
def cfn_specification_url():
    return "https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"

@pytest.fixture
def repository():
    return CfnSpecificationRepository(
        loader=RemoteFileLoader("https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json"),
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
    )

def test_CfnSpecificationRepository_get_resource_spec(repository:CfnSpecificationRepository):

    for resource_type in repository.spec.ResourceTypes.keys():
        resource_spec = repository.get_resource_spec(CfnSpecificationResourceTypeName(resource_type))
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
    invalid_key = CfnSpecificationResourceTypeName("AWS::Invalid::Key")
    with pytest.raises(KeyError) as ex:
        repository.get_resource_spec(invalid_key)
    assert invalid_key.fullname in ex.value.args 

def test_CfnSpecificationRepository_get_property_spec_KeyError(repository:CfnSpecificationRepository):
    invalid_key = CfnSpecificationPropertyTypeName("AWS::Invalid::Key.1")
    with pytest.raises(KeyError) as ex:
        repository.get_property_spec(invalid_key)
    assert invalid_key.fullname in ex.value.args 


def test_CfnSpecificationRepository_get_property_spec(repository:CfnSpecificationRepository):
    for property_type in repository.spec.PropertyTypes.keys():
        print(property_type)
        property_spec = repository.get_property_spec(CfnSpecificationPropertyTypeName(property_type))
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
    resource_type = CfnSpecificationResourceTypeName("AWS::EC2::Instance")
    proeprties = repository.list_properties_for_resource(resource_type)
    assert proeprties.get(CfnSpecificationPropertyTypeName(f"{resource_type.fullname}.BlockDeviceMapping").fullname)
    assert proeprties.get(CfnSpecificationPropertyTypeName(f"{resource_type.fullname}.Ebs").fullname)


def test_CfnSpecificationRepository_get_specs_for_resources(repository:CfnSpecificationRepository):
    resource_type = CfnSpecificationResourceTypeName("AWS::EC2::Instance")
    specs = repository.get_specs_for_resource(resource_type)
    assert specs.PropertySpecs.get(CfnSpecificationPropertyTypeName(f"{resource_type.fullname}.BlockDeviceMapping").fullname)
    assert specs.PropertySpecs.get(CfnSpecificationPropertyTypeName(f"{resource_type.fullname}.Ebs").fullname)

@pytest.mark.parametrize("resource_type,expected", [
    ("AWS::WAFv2::RuleGroup", True), ("AWS::EC2::Instance", False)
])
def test_CfnSpecificationRepository_is_recursive(resource_type:str, expected:bool, repository:CfnSpecificationRepository):
    assert repository.is_recursive(CfnSpecificationResourceTypeName(resource_type)) == expected
