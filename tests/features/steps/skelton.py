# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring

import json
import subprocess
from behave import then, when
from cfn_docgen.domain.model.cfn_specification import CfnSpecification

from environment import SkeltonContext

@when("cfn-docgen skelton subcommand is invoked, with specifying skelton type as custom-resource-specification")
def step_impl(context:SkeltonContext):
    result = subprocess.run(
        [
            "cfn-docgen", "skelton",
            "--type", context.type,
        ],
        check=True,
        capture_output=True,
    )
    assert result.returncode == 0
    context.stdout = result.stdout.decode(encoding="UTF-8")


@then("sample skelton for custom resource specification is show in stdout")
def step_impl(context:SkeltonContext):
    custom_spec = CfnSpecification(**json.loads(context.stdout))
    assert len(custom_spec.ResourceTypes) > 0
    assert len(custom_spec.PropertyTypes) > 0