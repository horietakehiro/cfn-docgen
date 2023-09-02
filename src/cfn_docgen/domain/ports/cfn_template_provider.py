from abc import ABC, abstractmethod
from typing import Callable
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_template import CfnTemplateDefinition, CfnTemplateSource

from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

class ICfnTemplateProvider(ABC):

    def __init__(
        self,
        file_loader_factory:Callable[[CfnTemplateSource, AppContext], IFileLoader],
        context:AppContext,
    ) -> None:
        self.context = context
        self.file_loader_factory = file_loader_factory

    @abstractmethod
    def load_template(self, template_source:CfnTemplateSource) -> CfnTemplateDefinition:
        """load cfn template file(either json or yaml format) as dict"""
