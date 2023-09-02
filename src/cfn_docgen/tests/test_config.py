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

    context.log_info("info")
    context.log_error("error")
    context.log_warning("warning")
    context.log_debug("debug")

    assert context.log_messages.info[0] == "info"
    assert context.log_messages.error[0] == "error"
    assert context.log_messages.warning[0] == "warning"
    assert context.log_messages.debug[0] == "debug"
    for msg, record in zip(["info", "error", "warning", "debug"], caplog.records):
        assert "test_AppContext_logging" == record.funcName
        assert msg == record.message


def test_AppContext_log_message():
    context = AppContext()

    context.log_info("info")
    context.log_error("error")
    context.log_warning("warning")
    context.log_debug("debug")
    context.log_debug("debug")

    for level, msg in zip(
        [logging.INFO, logging.WARNING, logging.ERROR],
        ["info", "warning", "error"]
    ):
        assert context.log_messages.as_string(level) == f"[{msg.upper()}] {msg}"
    assert context.log_messages.as_string(logging.DEBUG) == "[DEBUG] debug\n[DEBUG] debug"