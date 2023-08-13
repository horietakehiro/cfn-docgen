import pytest
from domain.model.cfn_specification import CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName


@pytest.mark.parametrize("resource_type", [
    ("AWS::EC2::Instance"), ("Custom::hoge::fuga")
])
def test_CfnSpecificationResourceType_valid(resource_type:str):
    t = CfnSpecificationResourceTypeName(resource_type)
    assert t.fullname == resource_type

@pytest.mark.parametrize("resource_type", [
    ("AWS::EC2::Instance.BlockDeviceMappings"), ("AWS::EC2"), ("hogefuga")
])
def test_CfnSpecificationResourceType_invalid(resource_type:str):
    with pytest.raises(AssertionError):
        CfnSpecificationResourceTypeName(resource_type)

@pytest.mark.parametrize("property_type,prefix,suffix", [
    ("AWS::EC2::Instance.BlockDeviceMapping", "AWS::EC2::Instance", "BlockDeviceMapping"),
    ("Custom::hoge::fuga.HOGEFUGA", "Custom::hoge::fuga", "HOGEFUGA"),
    ("Tag","Tag","Tag")
])
def test_CfnSpecificationPropertyType_valid(property_type:str, prefix:str, suffix:str):
    t = CfnSpecificationPropertyTypeName(property_type)
    assert t.fullname == property_type
    assert t.prefix == prefix
    assert t.suffix == suffix

@pytest.mark.parametrize("property_type", [
    ("AWS::EC2::Instance"), ("BlockDeviceMapping"), ("AWS::EC2::Instance.BlockDeviceMapping.Ebs")
])
def test_CfnSpecificationPropertyType_invalid(property_type:str):
    with pytest.raises(AssertionError):
        CfnSpecificationPropertyTypeName(property_type)