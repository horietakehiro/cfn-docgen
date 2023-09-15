import json
import logging
import os
import pytest
import requests
from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_specification import CfnSpecification, CfnSpecificationPropertyTypeName, CfnSpecificationResourceTypeName

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

@pytest.fixture(scope="class", autouse=False)
def original_specification():
    res = requests.get(AppConfig.DEFAULT_SPECIFICATION_URL)
    return CfnSpecification(**json.loads(res.content.decode()))

@pytest.fixture
def custom_specification():
    localpath = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "..", "docs", "custom-specification.json",
    )
    with open(localpath, "r", encoding="UTF-8") as fp:
        data = fp.read()
    return CfnSpecification(**json.loads(data))


@pytest.mark.parametrize("resource_type", [
    ("AWS::EC2::Instance"), ("Custom::hoge")
])
def test_CfnSpecificationResourceType_valid(resource_type:str, context:AppContext):
    t = CfnSpecificationResourceTypeName(resource_type, context=context)
    assert t.fullname == resource_type

@pytest.mark.parametrize("resource_type", [
    ("AWS::EC2::Instance.BlockDeviceMappings"), ("AWS::EC2"), ("hogefuga")
])
def test_CfnSpecificationResourceType_invalid(resource_type:str, context:AppContext):
    with pytest.raises(AssertionError):
        CfnSpecificationResourceTypeName(resource_type, context=context)

@pytest.mark.parametrize("property_type,prefix,suffix", [
    ("AWS::EC2::Instance.BlockDeviceMapping", "AWS::EC2::Instance", "BlockDeviceMapping"),
    ("Custom::hoge.HOGEFUGA", "Custom::hoge", "HOGEFUGA"),
    ("Tag","Tag","Tag")
])
def test_CfnSpecificationPropertyType_valid(
    property_type:str, prefix:str, suffix:str,
    context:AppContext,
):
    t = CfnSpecificationPropertyTypeName(property_type, context=context)
    assert t.fullname == property_type
    assert t.prefix == prefix
    assert t.suffix == suffix

@pytest.mark.parametrize("property_type", [
    ("AWS::EC2::Instance"), ("BlockDeviceMapping"), ("AWS::EC2::Instance.BlockDeviceMapping.Ebs")
])
def test_CfnSpecificationPropertyType_invalid(property_type:str, context:AppContext):
    with pytest.raises(AssertionError):
        CfnSpecificationPropertyTypeName(property_type, context=context)

def test_CfnSpecification_merge_with_custom_specification(
    original_specification:CfnSpecification,
    custom_specification:CfnSpecification,
    context:AppContext,
):

    assert "Custom::Resource" not in list(original_specification.ResourceTypes.keys())
    assert "Custom::Resource.NestedProp" not in list(original_specification.PropertyTypes.keys())
    assert "AWS::CloudFormation::CustomResource" in list(original_specification.ResourceTypes.keys())
    original_specification.merge_with_custom_specification(
        custom_specification=custom_specification,
        context=context,
    )

    assert "Custom::Resource" in list(original_specification.ResourceTypes.keys())
    assert "Custom::Resource.NestedProp" in list(original_specification.PropertyTypes.keys())
    assert "AWS::CloudFormation::CustomResource" in list(original_specification.ResourceTypes.keys())
