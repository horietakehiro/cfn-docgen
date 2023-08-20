import os
from typing import Any
from adapters.cfn_document_storage import CfnDocumentStorage
from adapters.internal.file_loader import document_loader_factory
from domain.model.cfn_document_generator import CfnDocumentDestination

OUTPUT_FILE="output.txt"

def teardown_function(function:Any):
    try:
        os.remove(OUTPUT_FILE)
    except FileNotFoundError:
        pass


def test_CfnDocumentStorage_save_document():

    storage = CfnDocumentStorage(
        document_loader_factory=document_loader_factory,
    )
    body = b"body"
    dest = CfnDocumentDestination(
        dest=OUTPUT_FILE,
    )
    storage.save_document(body, dest)

    with open(OUTPUT_FILE, "rb") as fp:
        assert fp.read() == body

