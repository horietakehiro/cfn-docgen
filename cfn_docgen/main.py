import os
import click

from cfn_docgen import util


class DefaultGroup(click.Group):

    ignore_unknown_options = True

    def __init__(self, *args, **kwargs):
        default_command = kwargs.pop('default_command', None)
        super(DefaultGroup, self).__init__(*args, **kwargs)
        self.default_cmd_name = None
        if default_command is not None:
            self.set_default_command(default_command)

    def set_default_command(self, command):
        if isinstance(command, str):
            cmd_name = command
        else:
            cmd_name = command.name
            self.add_command(command)
        self.default_cmd_name = cmd_name

    def parse_args(self, ctx, args):
        if not args and self.default_cmd_name is not None:
            args.insert(0, self.default_cmd_name)
        return super(DefaultGroup, self).parse_args(ctx, args)

    def get_command(self, ctx, cmd_name):
        if cmd_name not in self.commands and self.default_cmd_name is not None:
            ctx.args0 = cmd_name
            cmd_name = self.default_cmd_name
        return super(DefaultGroup, self).get_command(ctx, cmd_name)

    def resolve_command(self, ctx, args):
        cmd_name, cmd, args = super(DefaultGroup, self).resolve_command(ctx, args)
        args0 = getattr(ctx, 'args0', None)
        if args0 is not None:
            args.insert(0, args0)
        return cmd_name, cmd, args


@click.group(name="cfn-docgen", cls=DefaultGroup, default_command="docgen")
@click.version_option()
def main():
    pass

@main.command()
@click.option("--in", "in_filepath", required=True, help="Input cfn template file path (yaml/json)")
# @click.option("--out", "out_filepath", required=False, default=None, help="Output file path.")
@click.option("--fmt", "fmt", required=False, default="xlsx", help="Output file format.", type=click.Choice(["xlsx", "md", "csv", "html"]), show_default=True)
@click.option("--omit", required=False, default=False, is_flag=True, help="If set, optional properties whose actual values are not set in input template file will not be written in output file.",)
@click.option("--refresh", required=False, default=False, is_flag=True, help="If set, fristly remove all existing cache files and download them again.",)
@click.option("--region", required=False, default=None, help="AWS region name for referencing resource specs. If not set, the value set as environment variable `CFN_DOCGEN_AWS_REGION` is used. If the environment variable is not set, use the value of AWS CLI default profile")
@click.option("--style", required=False, default="white", help="Table style. Option white is available only when '--fmt' option is xsls.", type=click.Choice(["white", "blank", "all"]), show_default=True)
@click.option("--verbose", required=False, is_flag=True, help="If set, stdout DEBUG level logs")
def docgen(
    in_filepath:str, fmt="xlsx", omit:bool=False, refresh:bool=False, region:str=None, verbose:bool=False, style:str="white",
):
    """
    [Default Subcommand] generate document from cfn template files
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


@main.command()
@click.option("--resource-type", "resource_type" ,required=True, help="AWS CloudFormation resource type for generating metadata skelton (e.g. AWS::EC2::VPC)",)
@click.option("--recursive", "recursive", required=False, default=False, is_flag=True, help="if set, generate skelton recursively",)
@click.option("--fmt", "fmt", required=False, default="yaml", type=click.Choice(["yaml", "json"]), help="skelton format",show_default=True)
def skelton(resource_type:str, recursive:bool=False, fmt:str="yaml"):
    """
    stdout cfn-docgen metadata skelton for given resource type
    """
    from cfn_docgen.cfn_skelton import CfnSkelton
    s = CfnSkelton(resource_type, recursive)
    res = s.main()

    click.echo(res)
