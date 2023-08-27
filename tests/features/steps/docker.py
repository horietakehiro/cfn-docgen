# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring

import os
from behave import given, then, when

from tests.features.environment import DockerContext
from cfn_docgen import VERSION

@given("cfn-docgen docker image is installed locally")
def step_impl(context:DockerContext):
    context.docker_client.images.get(f"horietakehiro/cfn-docgen:{VERSION}") # type: ignore

@when("Invoke cfn-docgen as docker container")
def step_impl(context:DockerContext):
    context.docker_client.containers.run( # type: ignore
        f"horietakehiro/cfn-docgen:{VERSION}",
        command=f"docgen -f markdown -s {context.source} -d {context.dest}",
        remove=True,
        volumes={
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs") : {"bind": "/tmp/", "mode": "rw"},
            "/tmp/" : {"bind": "/out/", "mode": "rw"}
        }
    )

@then("markdown document files are created and saved locally")
def step_impl(context:DockerContext):
    print()
    with open(context.expected[0], "r") as fp:
        output = fp.read()
    with open(context.master, "r") as fp:
        expected = fp.read()

    assert output == expected
