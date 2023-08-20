from typing import Callable
from adapters.internal.file_loader import document_loader_factory
from domain.model.cfn_document_generator import CfnDocumentDestination
from domain.ports.cfn_document_storage import ICfnDocumentStorage
from domain.ports.internal.file_loader import IFileLoader

def document_storage_facotory(dest:CfnDocumentDestination) -> ICfnDocumentStorage:
    return CfnDocumentStorage(
        document_loader_factory=document_loader_factory,
    )

class CfnDocumentStorage(ICfnDocumentStorage):
    def __init__(self, document_loader_factory: Callable[[CfnDocumentDestination], IFileLoader]) -> None:
        self.document_loader_factory = document_loader_factory

    def save_document(self, body: bytes, document_dest: CfnDocumentDestination) -> None:
        loader = self.document_loader_factory(document_dest)
        loader.upload(body, document_dest.dest)

