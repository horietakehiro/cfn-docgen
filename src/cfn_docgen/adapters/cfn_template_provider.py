from typing import Callable
from cfn_flip import to_json # type: ignore
from cfn_docgen.adapters.internal.file_loader import template_loader_factory
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_template import CfnTemplateDefinition, CfnTemplateSource
from cfn_docgen.domain.ports.cfn_template_provider import ICfnTemplateProvider
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

def template_provider_factory(template_source:CfnTemplateSource, context:AppContext) -> ICfnTemplateProvider:
    context.log_debug(f"type of template source is [{template_source.type}]. return CfnTemplateProvider")
    return CfnTemplateProvider(
        file_loader_factory=template_loader_factory,
        context=context,
    )

class CfnTemplateProvider(ICfnTemplateProvider):
    def __init__(self, file_loader_factory: Callable[[CfnTemplateSource, AppContext], IFileLoader], context: AppContext) -> None:
        super().__init__(file_loader_factory, context)
        self.file_loader_factory = file_loader_factory

    def load_template(self, template_source:CfnTemplateSource) -> CfnTemplateDefinition:
        loader = self.file_loader_factory(template_source, self.context)
        template_bytes = loader.download(template_source.source)
        template_str = template_bytes.decode(encoding="UTF-8")
        if template_str.startswith("{") and template_str.endswith("}"):
            self.context.log_debug(f"template source [{template_source.source}] is json format")
            return CfnTemplateDefinition.from_string(template_str, context=self.context)
        
        self.context.log_debug(f"template source [{template_source.source}] is yaml format")
        return CfnTemplateDefinition.from_string(to_json(template_str), context=self.context)