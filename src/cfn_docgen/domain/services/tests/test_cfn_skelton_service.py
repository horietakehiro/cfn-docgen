
import json
import logging
import os
from cfn_flip import to_json # type: ignore
import pytest
from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory

from cfn_docgen.config import AppConfig, AppContext
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationResourceTypeName
from cfn_docgen.domain.model.cfn_template import CfnTemplateResourceDefinition
from cfn_docgen.domain.services.cfn_skeleton_service import CfnSkeletonService, CfnSkeletonServiceCommandInput, SkeletonFormat

CUSTOM_RESOURCE_SPECIFICATION=os.path.join(
    os.path.dirname(__file__),
    "..", "..","..", "..","..", "docs", "custom-specification.json"
)

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG
    )

@pytest.fixture
def repository(context:AppContext):
    return CfnSpecificationRepository(
        source_url=AppConfig.DEFAULT_SPECIFICATION_URL,
        custom_resource_specification_url=CUSTOM_RESOURCE_SPECIFICATION,
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        context=context,
    )

def test_CfnSkeletonService_list_resource_types(
    repository:CfnSpecificationRepository,
    context:AppContext
):
    service = CfnSkeletonService(
        cfn_specification_repository=repository,
        context=context,
    )
    command_input = CfnSkeletonServiceCommandInput(
        type=None,
        list=True,
    )

    command_output = service.main(command_input)
    assert "AWS::EC2::Instance" in command_output.skeleton
    assert "Custom::Resource" in command_output.skeleton


@pytest.mark.parametrize("resource_type,fmt", [
    ("AWS::IAM::Role", "yaml"),
    ("AWS::IAM::Role", "json"),
    ("Custom::Resource", "yaml"),
    ("Custom::Resource", "json"),
])
def test_CfnSkeletonService_resource_skeleton(
    resource_type:str,fmt:SkeletonFormat,
    repository:CfnSpecificationRepository,
    context:AppContext
):
    service = CfnSkeletonService(
        cfn_specification_repository=repository,
        context=context,
    )
    command_input = CfnSkeletonServiceCommandInput(
        type=CfnSpecificationResourceTypeName(resource_type, context),
        format=fmt,
        list=False,
    )

    command_output = service.main(command_input)

    if fmt == "json":
        assert command_output.skeleton.startswith("{")
        assert command_output.skeleton.endswith("}")
        CfnTemplateResourceDefinition(**json.loads(command_output.skeleton))

    if fmt == "yaml":
        assert f"Type: {resource_type}"
        _ = CfnTemplateResourceDefinition(
            **json.loads(to_json(command_output.skeleton))
        )

def test_CfnSkeletonService_resource_skeleton_error(
    repository:CfnSpecificationRepository,
    context:AppContext
):
    service = CfnSkeletonService(
        cfn_specification_repository=repository,
        context=context,
    )
    command_input = CfnSkeletonServiceCommandInput(
        type=CfnSpecificationResourceTypeName("Custom::NotExist", context),
        format="yaml",
        list=False,
    )

    with pytest.raises(Exception):
        _ = service.main(command_input)

