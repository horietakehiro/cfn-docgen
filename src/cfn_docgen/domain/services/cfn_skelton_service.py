from dataclasses import dataclass
import json
from cfn_docgen.config import AppContext

@dataclass
class CfnSkeltonServiceCommandInput:
    type: str
@dataclass
class CfnSkeltonServiceCommandOutput:
    skelton: str


class CfnSkeltonService:

    def __init__(self, context:AppContext) -> None:
        self.context = context

    def main(self, command_input:CfnSkeltonServiceCommandInput) -> CfnSkeltonServiceCommandOutput:
        self.context.log_debug(f"received skelton type is [{command_input.type}]")
        if command_input.type == "custom-resource-specification":
            skelton = json.dumps(
                {
                    "ResourceSpecificationVersion": "0.0.0",
                    "PropertyTypes": {
                        "Custom::Resource.NestedProp": {
                            "Documentation": None,
                            "Properties": {
                                "NumberProp": {
                                    "Documentation": None,
                                    "UpdateType": "Mutable",
                                    "Required": True,
                                    "PrimitiveType": "Integer"
                                },
                                "BoolProp": {
                                    "Documentation": None,
                                    "UpdateType": "Mutable",
                                    "Required": True,
                                    "PrimitiveType": "Boolean"
                                }
                            }
                        }
                    },
                    "ResourceTypes": {
                        "Custom::Resource": {
                            "AdditionalProperties": True,
                            "Documentation": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html",
                            "Properties": {
                                "ServiceToken": {
                                    "Documentation": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html#cfn-customresource-servicetoken",
                                    "PrimitiveType": "String",
                                    "Required": True,
                                    "UpdateType": "Immutable"
                                },
                                "StringProp": {
                                    "Documentation": None,
                                    "PrimitiveType": "String",
                                    "Required": True,
                                    "UpdateType": "Mutable"
                                },
                                "NestedProp": {
                                    "Documentation": None,
                                    "Required": True,
                                    "UpdateType": "Mutable",
                                    "Type": "NestedProp"
                                }
                            }
                        }
                    }
                },
                indent=2,
                ensure_ascii=False,
            )
            return CfnSkeltonServiceCommandOutput(
                skelton=skelton,
            )
        
        self.context.log_error(
            f"received skelton type [{command_input.type}] is not supported"
        )
        raise NotImplementedError
