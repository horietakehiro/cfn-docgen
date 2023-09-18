from dataclasses import dataclass
import json
from typing import Literal, Optional
from cfn_flip import to_yaml # type: ignore

from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationResourceTypeName
from cfn_docgen.domain.model.cfn_template import CfnTemplateResourceDefinition, CfnTemplateResourceNode, ResourceInfo
from cfn_docgen.domain.ports.cfn_specification_repository import ICfnSpecificationRepository

SkeltonFormat = Literal["yaml", "json"]

@dataclass
class CfnSkeltonServiceCommandInput:
    type: Optional[CfnSpecificationResourceTypeName]
    list: bool
    format: SkeltonFormat = "yaml"

@dataclass
class CfnSkeltonServiceCommandOutput:
    skelton: str
    type: Optional[str] = None
    document_url:Optional[str] = None


class CfnSkeltonService:

    def __init__(self, cfn_specification_repository:ICfnSpecificationRepository, context:AppContext) -> None:
        self.spec_repository = cfn_specification_repository
        self.context = context

    def main(self, command_input:CfnSkeltonServiceCommandInput) -> CfnSkeltonServiceCommandOutput:
        self.context.log_debug(f"received skelton type is [{command_input.type}]")

        try:
            if command_input.list:
                self.context.log_debug("list supported resource types")
                resource_types = self.spec_repository.list_resource_types()
                command_output = CfnSkeltonServiceCommandOutput(
                    skelton="\n".join(resource_types)
                )
                return command_output
        
            if command_input.type is None:
                raise ValueError("you must specify resource type")
            
            self.context.log_debug(f"generate skelton for resource type [{command_input.type.fullname}]")

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

            resource_skelton = resource_node.as_skelton()
            dumped_resource_skelton = json.dumps(resource_skelton, indent=2, ensure_ascii=False)
            if command_input.format == "yaml":
                dumped_resource_skelton = to_yaml(dumped_resource_skelton)

            command_output = CfnSkeltonServiceCommandOutput(
                skelton=dumped_resource_skelton,
                type=command_input.type.fullname,
                document_url=specs.ResourceSpec.Documentation,
            )

            return command_output

        except Exception as ex:
            self.context.log_error(
                f"generate skelton failed for resource type [{command_input.type}]"
            )
            raise ex
