# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring

import json
import subprocess
from behave import then, when
from cfn_docgen.domain.model.cfn_template import CfnTemplateResourceDefinition

from environment import SkeletonContext

@when("cfn-docgen skeleton subcommand is invoked, with specifying resource type")
def step_impl(context:SkeletonContext):
    result = subprocess.run(
        [
            "cfn-docgen", "skeleton",
            "--type", context.type,
            "--format", "json"
        ],
        check=True,
        capture_output=True,
    )
    assert result.returncode == 0
    context.stdout = result.stdout.decode(encoding="UTF-8")


@then("skeleton for the resource type is show in stdout")
def step_impl(context:SkeletonContext):
    definition = CfnTemplateResourceDefinition(**json.loads(context.stdout))
    assert definition.Type == context.type