from abc import ABC, abstractmethod
from typing import Callable
from domain.model.cfn_document_generator import CfnDocumentDestination

from domain.ports.internal.file_loader import IFileLoader


class ICfnDocumentStorage(ABC):

    def __init__(self, document_loader_factory:Callable[[CfnDocumentDestination], IFileLoader]) -> None:
        self.document_loader_factory = document_loader_factory

    @abstractmethod
    def save_document(self, body:bytes, document_dest:CfnDocumentDestination) -> None:
        pass