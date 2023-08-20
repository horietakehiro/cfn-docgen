from typing import Callable
from cfn_flip import to_json # type: ignore
from adapters.internal.file_loader import file_loader_factory # type: ignore
from domain.model.cfn_template import CfnTemplateDefinition, CfnTemplateSource
from domain.ports.cfn_template_provider import ICfnTemplateProvider
from domain.ports.internal.file_loader import IFileLoader

def template_provider_factory(template_source:CfnTemplateSource) -> ICfnTemplateProvider:
    return CfnTemplateProvider(
        file_loader_factory=file_loader_factory,
    )

class CfnTemplateProvider(ICfnTemplateProvider):
    def __init__(self, file_loader_factory:Callable[[CfnTemplateSource], IFileLoader]) -> None:
        self.file_loader_factory = file_loader_factory

    def load_template(self, template_source:CfnTemplateSource) -> CfnTemplateDefinition:
        loader = self.file_loader_factory(template_source)
        template_bytes = loader.download(template_source.source)
        template_str = template_bytes.decode(encoding="UTF-8")
        if template_str.startswith("{") and template_str.endswith("}"):
            return CfnTemplateDefinition.from_string(template_str)
        return CfnTemplateDefinition.from_string(to_json(template_str))