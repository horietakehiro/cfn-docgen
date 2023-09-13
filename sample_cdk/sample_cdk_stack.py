# pyright: reportUnknownArgumentType=false,reportUnknownParameterType=false
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    
)
from constructs import Construct
from typing import Any
from cfn_docgen.domain.model.cfn_template import (
    CfnTemplateMetadataCfnDocgenDefinition as Metadata,
    CfnTemplateResourceMetadataDefinition as ResourceMetadata,
    CfnTemplateResourceMetadataCfnDocgenDefinition as CfnDocgen
)
class CfnDocgenSampleCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs:Any) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.add_metadata(
            "CfnDocgen", Metadata(
                Description="top-level-description"
            ).model_dump(),
        )
        self.vpc_construct = ec2.Vpc(self, "VpcConstruct", max_azs=1)
        self.vpc_construct.node.default_child.cfn_options.metadata = ResourceMetadata( # type: ignore
            CfnDocgen=CfnDocgen(Description="resource-level-description")
        ).model_dump()