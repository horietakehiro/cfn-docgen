from dataclasses import dataclass
import json
from typing import Literal, Optional
from cfn_flip import to_yaml # type: ignore

from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationResourceTypeName
from cfn_docgen.domain.model.cfn_template import CfnTemplateResourceDefinition, CfnTemplateResourceNode, ResourceInfo
from cfn_docgen.domain.ports.cfn_specification_repository import ICfnSpecificationRepository

SkeletonFormat = Literal["yaml", "json"]

@dataclass
class CfnSkeletonServiceCommandInput:
    type: Optional[CfnSpecificationResourceTypeName]
    list: bool
    format: SkeletonFormat = "yaml"

@dataclass
class CfnSkeletonServiceCommandOutput:
    skeleton: str
    type: Optional[str] = None
    document_url:Optional[str] = None


class CfnSkeletonService:

    def __init__(self, cfn_specification_repository:ICfnSpecificationRepository, context:AppContext) -> None:
        self.spec_repository = cfn_specification_repository
        self.context = context

    def main(self, command_input:CfnSkeletonServiceCommandInput) -> CfnSkeletonServiceCommandOutput:
        self.context.log_debug(f"received skeleton type is [{command_input.type}]")

        try:
            if command_input.list:
                self.context.log_debug("list supported resource types")
                resource_types = self.spec_repository.list_resource_types()
                command_output = CfnSkeletonServiceCommandOutput(
                    skeleton="\n".join(resource_types)
                )
                return command_output
        
            if command_input.type is None:
                raise ValueError("you must specify resource type")
            
            self.context.log_debug(f"generate skeleton for resource type [{command_input.type.fullname}]")

            # create resource node for the resource type
            specs = self.spec_repository.get_specs_for_resource(command_input.type)
            resource_node = CfnTemplateResourceNode(
                definition=CfnTemplateResourceDefinition(
                    Type=command_input.type.fullname,
                    Properties={},
                ),
                resource_info=ResourceInfo(
                    type=command_input.type.fullname,
                    is_recursive=self.spec_repository.is_recursive(command_input.type),
                ),
                specs=specs,
                context=self.context,
            )

            resource_skeleton = resource_node.as_skeleton()
            dumped_resource_skeleton = json.dumps(resource_skeleton, indent=2, ensure_ascii=False)
            if command_input.format == "yaml":
                dumped_resource_skeleton = to_yaml(dumped_resource_skeleton)

            command_output = CfnSkeletonServiceCommandOutput(
                skeleton=dumped_resource_skeleton,
                type=command_input.type.fullname,
                document_url=specs.ResourceSpec.Documentation,
            )

            return command_output

        except Exception as ex:
            self.context.log_error(
                f"generate skeleton failed for resource type [{command_input.type}]"
            )
            raise ex
