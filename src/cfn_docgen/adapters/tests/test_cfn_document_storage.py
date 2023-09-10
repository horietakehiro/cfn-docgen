import logging
import os
from typing import Any

import pytest
from cfn_docgen.adapters.cfn_document_storage import CfnDocumentStorage
from cfn_docgen.adapters.internal.file_loader import document_loader_factory
from cfn_docgen.config import AppContext, AwsConnectionSettings, ConnectionSettings
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination

OUTPUT_FILE=os.path.join(
    os.path.dirname(__file__), "output.txt"
)

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

def teardown_function(function:Any):
    try:
        os.remove(OUTPUT_FILE)
    except FileNotFoundError:
        pass


def test_CfnDocumentStorage_save_document(context:AppContext):

    storage = CfnDocumentStorage(
        document_loader_factory=document_loader_factory,
        context=context,
    )
    body = b"body"
    dest = CfnDocumentDestination(
        dest=OUTPUT_FILE,
        context=context,
    )
    storage.save_document(body, dest)

    with open(OUTPUT_FILE, "rb") as fp:
        assert fp.read() == body

