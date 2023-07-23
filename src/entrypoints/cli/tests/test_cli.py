import pytest
import os
import shutil
import difflib
from click.testing import CliRunner

from src.entrypoints.cli.main import main
from src.entrypoints.cli.model.cli_model import CliArguement


@pytest.fixture
def input_file():
    return os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "docs", "sample-template.yaml"
    )

@pytest.fixture
def output_dir():
    return os.path.join(
        os.path.dirname(__file__), "data",
    )

@pytest.fixture
def example_markdown_file():
    return os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "docs", "sample-template.md"
    )

def setup_function(function): # type:ignore

    # flush test output directory
    d = os.path.join(
        os.path.dirname(__file__), "data",
    )
    try:
        shutil.rmtree(d)
    except FileNotFoundError:
        pass
    os.makedirs(d, exist_ok=True)        

def test_cli_success(input_file:str, output_dir:str, example_markdown_file:str):
    output_file = os.path.join(output_dir, "sample-template.md")
    
    args = CliArguement(
        subcommand="docgen",
        format="markdown",
        input_file=input_file,
        output_file=output_file,
    )

    runner = CliRunner()
    result = runner.invoke(main, args=args.as_list())
    
    assert result.exit_code == 0
    assert output_file in result.output

    with open(output_file, "r", encoding="UTF-8") as fp:
        output_lines = fp.readlines()
    with open(example_markdown_file, "r", encoding="UTF-8") as fp:
        example_lines = fp.readlines()
    
    assert "\n".join(output_lines) == "\n".join(example_lines), difflib.unified_diff(
        output_lines, example_lines,
        fromfile=output_file, tofile=example_markdown_file,
    )




