# pyright: reportGeneralTypeIssues=false
# pylint: disable=missing-function-docstring

import logging
from behave import given, then, when
from cfn_docgen.config import AppContext, AwsConnectionSettings, ConnectionSettings

from tests.features.environment import PackageContext

@given("cfn-docgen package is installed locally")
def step_impl(context:PackageContext):
    import cfn_docgen # type: ignore

@when("Invoke cfn-docgen from python code")
def step_impl(context:PackageContext):
    app_context = AppContext(
        log_level=logging.CRITICAL,
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )
    from cfn_docgen import (
        CfnDocgenService, CfnDocgenServiceCommandInput,
        CfnTemplateSource, CfnDocumentDestination
    )
    service = CfnDocgenService.with_default()
    service.main(
        command_input=CfnDocgenServiceCommandInput(
            template_source=CfnTemplateSource(context.source, context=app_context),
            document_dest=CfnDocumentDestination(context.dest, context=app_context),
            fmt=context.format,
        )
    )

@then("markdown document files are created")
def step_impl(context:PackageContext):

    with open(context.dest, "r") as fp:
        output = fp.read()
    with open(context.expected[0], "r") as fp:
        expected = fp.read()

    assert output == expected