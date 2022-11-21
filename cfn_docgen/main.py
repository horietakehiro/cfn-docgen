import os
import click

from cfn_docgen import util

@click.command(name="cfn-docgen")
@click.option("--in", "in_filepath", required=True, help="Input cfn template file path (yaml/json)")
# @click.option("--out", "out_filepath", required=False, default=None, help="Output file path.")
@click.option("--fmt", "fmt", required=False, default="xlsx", help="Output file format.", type=click.Choice(["xlsx", "md", "csv", "html"]), show_default=True)
@click.option("--omit", required=False, default=False, is_flag=True, help="If set, optional properties whose actual values are not set in input template file will not be written in output file.",)
@click.option("--refresh", required=False, default=False, is_flag=True, help="If set, fristly remove all existing cache files and download them again.",)
@click.option("--region", required=False, default=None, help="AWS region name for referencing resource specs. If not set, the value set as environment variable `CFN_DOCGEN_AWS_REGION` is used. If the environment variable is not set, use the value of AWS CLI default profile")
@click.option("--style", required=False, default="white", help="Table style. Option white is available only when '--fmt' option is xsls.", type=click.Choice(["white", "blank", "all"]), show_default=True)
@click.option("--verbose", required=False, is_flag=True, help="If set, stdout DEBUG level logs")
@click.version_option()
def main(
    in_filepath:str, fmt="xlsx", omit:bool=False, refresh:bool=False, region:str=None, verbose:bool=False, style:str="white",
):
    """
    Document generator from cfn template files
    """

    os.environ["CFN_DOCGEN_VERBOSE"] = str(verbose).upper()
    logger = util.get_module_logger(__name__, verbose=verbose)
    logger.info("start process")

    if refresh:
        util.remove_cache()
        logger.info(f"remove all caches at {util.CACHE_BASE_DIR}")
    
    
    if region is not None:
        os.environ["CFN_DOCGEN_AWS_REGION"] = region



    from cfn_docgen import cfn_def
    # cfn_def.CfnTemplate.reload_specs()
    template = cfn_def.CfnTemplate(
        filepath=in_filepath, omit=omit, style=style,
    )
    template.to_file(None, fmt)

    logger.info("end propcess")



