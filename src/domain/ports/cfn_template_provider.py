from abc import ABC, abstractmethod
from typing import Callable
from src.domain.model.cfn_template import CfnTemplateDefinition, CfnTemplateSource

from domain.ports.internal.file_loader import IFileLoader

class ICfnTemplateProvider(ABC):

    def __init__(self, file_loader_factory:Callable[[CfnTemplateSource], IFileLoader]) -> None:
        self.file_loader_factory = file_loader_factory

    @abstractmethod
    def load_template(self, template_source:CfnTemplateSource) -> CfnTemplateDefinition:
        """load cfn template file(either json or yaml format) as dict"""

    # @abstractmethod
    # def save_document(self, document:str, document_destination:CfnDocumentDestination):
    #     """save generated document to the destination"""
