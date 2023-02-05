import pytest 

from cfn_docgen import main
from click.testing import CliRunner

import json

def test_main_skelton_default():

    runner = CliRunner()
    result = runner.invoke(
        main.main, ["skelton", "--resource-type", "AWS::EC2::VPC"], color=True,
    )

    assert result.exit_code == 0, result.exc_info
    assert "Tags:" in result.output
    assert "- Key:" not in result.output
    assert "Metadata:" in result.output
    assert "Properties:" not in result.output

def test_main_skelton_recursive():

    runner = CliRunner()
    result = runner.invoke(
        main.main, ["skelton", "--resource-type", "AWS::EC2::VPC", "--recursive"], color=True,
    )

    assert result.exit_code == 0, result.exc_info
    assert "Tags:" in result.output
    assert "- Key:" in result.output
    assert "Metadata:" in result.output
    assert "Properties:" not in result.output

def test_main_skelton_json():
    runner = CliRunner()
    result = runner.invoke(
        main.main, ["skelton", "--resource-type", "AWS::EC2::VPC", "--fmt", "json"], color=True,
    )

    assert result.exit_code == 0, result.exc_info
    assert isinstance(json.loads(result.output), dict)

def test_main_skelton_section_all():
    runner = CliRunner()
    result = runner.invoke(
        main.main, ["skelton", "--resource-type", "AWS::EC2::VPC", "--section", "all"], color=True,
    )

    assert result.exit_code == 0, result.exc_info
    assert "Metadata:" in result.output
    assert "Properties:" in result.output
    assert "List of Tag" in result.output

def test_main_skelton_section_properties():
    runner = CliRunner()
    result = runner.invoke(
        main.main, ["skelton", "--resource-type", "AWS::EC2::VPC", "--section", "properties"], color=True,
    )

    assert result.exit_code == 0, result.exc_info
    assert "Metadata:" not in result.output
    assert "Properties:" in result.output
    assert "List of Tag" in result.output
