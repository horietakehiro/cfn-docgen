import click

from src.entrypoints.cli.model.cli_model import SupportedFormat
from src.domain.services

@click.group(name="cfn-docgen")
@click.version_option()
def main():
    pass

@main.command()
@click.option("--format", "fmt", required=True, type=click.Choice(["markdown"]), help="format of output file")
@click.option("--input-file", "input_file", required=True, type=str, help="local filepath of input file")
@click.option("--output-file", "output_file", required=True, type=str, help="local filepath of output file")
def docgen(fmt:SupportedFormat, input_file:str, output_file:str):
    pass