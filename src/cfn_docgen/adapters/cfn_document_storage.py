from typing import Callable
from cfn_docgen.adapters.internal.file_loader import document_loader_factory
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.ports.cfn_document_storage import ICfnDocumentStorage
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

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

