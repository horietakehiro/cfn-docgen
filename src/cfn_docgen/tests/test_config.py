import logging
import re

import pytest
from cfn_docgen.config import AppContext


def test_AppContext_default():
    context = AppContext()
    assert re.match(
        pattern=r"^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}$",
        string=context.request_id,
    ) is not None

def test_AppContext_any_id():
    request_id = "any-id"
    context = AppContext(request_id=request_id)

    assert context.request_id == request_id

def test_AppContext_logging(caplog:pytest.LogCaptureFixture):
    caplog.set_level(logging.DEBUG)
    context = AppContext(log_level=logging.DEBUG)

    context.log_warning("warning")
    context.log_info("info")
    context.log_error("error")
    context.log_debug("debug")

    assert context.log_messages.messages[0].message == "warning"
    assert context.log_messages.messages[1].message == "info"
    assert context.log_messages.messages[2].message == "error"
    assert context.log_messages.messages[3].message == "debug"

    for msg, record in zip(["warning", "info", "error", "debug"], caplog.records):
        assert "test_AppContext_logging" == record.funcName
        assert msg == record.message


def test_AppContext_log_message():
    context = AppContext(log_level=logging.INFO)

    context.log_info("info")
    context.log_warning("warning")
    context.log_error("error")
    context.log_warning("warning")
    context.log_debug("debug")

    log_string = context.log_messages.as_string(logging.INFO)
    expected = "[INFO] info\n[WARNING] warning\n[ERROR] error\n[WARNING] warning"
    assert log_string == expected