# pylint: disable=W0621
from typing import Callable
from cfn_docgen.adapters.internal.file_loader import document_loader_factory
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.ports.cfn_document_storage import ICfnDocumentStorage
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

def document_storage_facotory(dest:CfnDocumentDestination, context:AppContext) -> ICfnDocumentStorage:
    context.log_debug(f"return CfnDocumentStorage for dest [{dest}]")
    return CfnDocumentStorage(
        document_loader_factory=document_loader_factory,
        context=context,
    )

class CfnDocumentStorage(ICfnDocumentStorage):
    def __init__(
        self, 
        document_loader_factory: Callable[[CfnDocumentDestination, AppContext],IFileLoader],
        context: AppContext,
    ) -> None:
        super().__init__(document_loader_factory, context)

    def save_document(self, body: bytes, document_dest: CfnDocumentDestination) -> None:
        loader = self.document_loader_factory(document_dest, self.context)
        loader.upload(body, document_dest.dest)
        self.context.log_debug(f"save document to [{document_dest.dest}]")