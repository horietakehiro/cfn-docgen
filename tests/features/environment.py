# type: ignore
from dataclasses import dataclass
from typing import Any, TypedDict
from behave import fixture
from behave.fixture import use_fixture_by_tag
import os

TEST_DATA_DIR=os.path.join(
    os.path.dirname(__file__), "data"
)

@dataclass
class CommandLineToolContext:
    format:str
    input_file:str
    output_file:str


@fixture
def command_line_tool(context:CommandLineToolContext, fmt:str, *args, **kwargs):
    context.format = fmt
    context.input_file = os.path.join(
        TEST_DATA_DIR, "inputs", "sample-template.yaml",
    )
    ext = ""
    match fmt:
        case "markdown":
            ext = "md"
        case _:
            pass
    context.output_file = os.path.join(
        TEST_DATA_DIR, "outputs", f"sample-template.{ext}"
    )
    yield context


fixture_registry = {
    "fixture.command_line_tool.markdown.single_file": (command_line_tool, ["markdown"], {})
}

def before_tag(context:Any, tag:str):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry)

