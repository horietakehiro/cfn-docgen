# type: ignore
from dataclasses import dataclass
from typing import Any, TypedDict
from behave import fixture
from behave.fixture import use_fixture_by_tag
import os
import shutil

TEST_DATA_DIR=os.path.join(
    os.path.dirname(__file__), "data"
)
DOCUMENT_DIR=os.path.join(
    os.path.dirname(__file__), "..", "..", "docs"
)

@dataclass
class CommandLineToolContext:
    format:str
    input_file:str
    output_file:str
    example_file: str


@fixture
def command_line_tool(context:CommandLineToolContext, fmt:str, *args, **kwargs):

    output_dir = os.path.join(TEST_DATA_DIR, "outputs")
    try:
        shutil.rmtree(output_dir)
    except FileNotFoundError:
        pass
    os.makedirs(output_dir, exist_ok=True)

    context.format = fmt
    context.input_file = os.path.join(
        DOCUMENT_DIR, "sample-template.yaml",
    )
    ext = ""
    match fmt:
        case "markdown":
            ext = "md"
        case _:
            pass
    context.output_file = os.path.join(
        output_dir, f"sample-template.{ext}"
    )
    context.example_file = os.path.join(
        DOCUMENT_DIR, f"sample-template.{ext}"
    )
    yield context


fixture_registry = {
    "fixture.command_line_tool.markdown.single_file": (command_line_tool, ["markdown"], {})
}

def before_tag(context:Any, tag:str):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry)

