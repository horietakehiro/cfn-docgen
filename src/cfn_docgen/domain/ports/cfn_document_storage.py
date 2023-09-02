from abc import ABC, abstractmethod
from typing import Callable
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination

from cfn_docgen.domain.ports.internal.file_loader import IFileLoader


class ICfnDocumentStorage(ABC):

    def __init__(
        self, 
        document_loader_factory:Callable[[CfnDocumentDestination, AppContext], IFileLoader],
        context:AppContext,
    ) -> None:
        self.context = context
        self.document_loader_factory = document_loader_factory

    @abstractmethod
    def save_document(self, body:bytes, document_dest:CfnDocumentDestination) -> None:
        pass