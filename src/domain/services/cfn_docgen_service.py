from src.domain.ports.cfn_template_provider import ICfnTemplateProvider
from src.domain.ports.logger import ILogger

class CfnDocgenService(object):

    def __init__(self, 
        cfn_template_provider:ICfnTemplateProvider,
        cfn_specification_repository:ICfnSpecificationRepository,
        logger:ILogger,
    ) -> None:
        # load template definition
        cfn_template_definition = cfn_template_provider.load_template()

        # parse template into object



        # convet object into some format of string

        # 