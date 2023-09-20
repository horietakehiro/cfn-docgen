import logging
from typing import Mapping
import pytest

from cfn_docgen.adapters.cfn_specification_repository import CfnSpecificationRepository
from cfn_docgen.adapters.internal.cache import LocalFileCache
from cfn_docgen.adapters.internal.file_loader import specification_loader_factory
from cfn_docgen.config import AppConfig, AppContext
from cfn_docgen.domain.model.cfn_template import CfnTemplateResourceDefinition, CfnTemplateResourcesNode

context = AppContext(log_level=logging.ERROR)
spec_repository_by_regions:Mapping[str, CfnSpecificationRepository] = {
    region: CfnSpecificationRepository(
        source_url=url,
        custom_resource_specification_url=None,
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
        context=context,
    ) for region, url in AppConfig.SPECIFICATION_URL_BY_REGION.items()
}
def all_resource_types(region:str, context:AppContext):
    spec_repository = CfnSpecificationRepository(
        context=context,
        source_url=AppConfig.SPECIFICATION_URL_BY_REGION.get(
            region, AppConfig.DEFAULT_SPECIFICATION_URL,
        ),
        loader_factory=specification_loader_factory,
        cache=LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context),
        recursive_resource_types=AppConfig.RECURSIVE_RESOURCE_TYPES,
    )
    return list(spec_repository.spec.ResourceTypes.keys())

@pytest.mark.parametrize("region,resource_type", [
    (
        region,
        resource_type
    ) 
    for region in AppConfig.SPECIFICATION_URL_BY_REGION.keys()
    for resource_type in all_resource_types(region, context=context)
])
def test_CfnTemplateResourcesNode_all_resource_types(
    region:str,
    resource_type:str,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    spec_repository = spec_repository_by_regions[region]

    definitions:Mapping[str, CfnTemplateResourceDefinition] = {
        resource_type: CfnTemplateResourceDefinition(
            Type=resource_type,
            Properties={}
        )
    }

    resources_node = CfnTemplateResourcesNode(
        definitions=definitions,
        spec_repository=spec_repository,
        context=context,
        resource_groups={},
    )

    resource_node = resources_node.group_nodes[resources_node.group_name_for_independent_resources].resource_nodes.get(resource_type)
    assert resource_node is not None
    assert resource_node.spec is not None
    properties_node = resource_node.properties_node
    assert (
        len(properties_node.property_leaves) > 0
        or len(properties_node.property_nodes) > 0
        or len(properties_node.property_nodes_list) > 0
        or len(properties_node.property_nodes_map)> 0
        # resource types without any properties
        or resource_type == "AWS::CloudFormation::WaitConditionHandle"
        or resource_type == "AWS::DevOpsGuru::LogAnomalyDetectionIntegration"
    )

    messages = [r.message for r in caplog.records]
    assert len(messages) == 0