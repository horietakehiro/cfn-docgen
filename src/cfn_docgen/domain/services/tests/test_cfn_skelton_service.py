
import json
import logging
import pytest

from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_specification import CfnSpecification
from cfn_docgen.domain.services.cfn_skelton_service import CfnSkeltonService, CfnSkeltonServiceCommandInput


@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG
    )

def test_CfnSkeltonService_custom_resource_specification(
    context:AppContext
):
    service = CfnSkeltonService(context=context)
    command_input = CfnSkeltonServiceCommandInput(
        type="custom-resource-specification"
    )

    CfnSpecification(**json.loads(service.main(command_input).skelton))


def test_CfnSkeltonService_not_supported(
    context:AppContext
):
    service = CfnSkeltonService(context=context)
    command_input = CfnSkeltonServiceCommandInput(
        type="not-supproted"
    )

    with pytest.raises(NotImplementedError):
        service.main(command_input)

