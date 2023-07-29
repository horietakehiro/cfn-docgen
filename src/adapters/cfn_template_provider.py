from domain.model.cfn_template import CfnTemplateDefinition
from domain.ports.cfn_template_provider import ICfnTemplateProvider
from domain.ports.file_loader import IFileLoader


class CfnTemplateProvider(ICfnTemplateProvider):
    def __init__(self, file_loader: IFileLoader) -> None:
        self.file_loader = file_loader
    
    def load_template(self) -> CfnTemplateDefinition:
        cfn_template_definition = self.file_loader.load()
        return CfnTemplateDefinition.from_string(cfn_template_definition)
    