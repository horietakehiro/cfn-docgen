from dataclasses import dataclass
import importlib
from logging import DEBUG, INFO

from src.adapters import logger

@dataclass
class Caplog:
    text: str

def setup_function(function): # type: ignore
    importlib.reload(logger)

def test_JsonStreamLogger_info(caplog:Caplog):

    l = logger.JsonStreamLogger("unit-test", INFO)
    l.info("info message")
    l.warning("warning message")
    l.error("error message")
    l.debug("debug message")

    assert "info message" in caplog.text
    assert "warning message" in caplog.text
    assert "error message" in caplog.text
    assert "debug message" not in caplog.text

def test_JsonStreamLogger_debug(caplog:Caplog):
    l = logger.JsonStreamLogger("unit-test", DEBUG)
    l.info("info message")
    l.warning("warning message")
    l.error("error message")
    l.debug("debug message")

    assert "info message" in caplog.text
    assert "warning message" in caplog.text
    assert "error message" in caplog.text
    assert "debug message" in caplog.text