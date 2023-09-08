from cfn_docgen.domain.model.cfn_document_generator import (
    CfnDocumentDestination as __CfnDocumentDestination
)
from cfn_docgen.domain.services.cfn_docgen_service import (
    CfnDocgenService as __CfnDocgenService,
    CfnDocgenServiceCommandInput as __CfnDocgenServiceCommandInput,
    CfnTemplateSource as __CfnTemplateSource
)


VERSION="0.9.0"

CfnDocgenService = __CfnDocgenService
CfnDocgenServiceCommandInput = __CfnDocgenServiceCommandInput
CfnTemplateSource = __CfnTemplateSource
CfnDocumentDestination = __CfnDocumentDestination