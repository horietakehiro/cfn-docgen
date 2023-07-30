from abc import ABC, abstractmethod
from typing import Callable, Optional
from src.domain.model.cfn_template import CfnTemplateDefinition

from src.domain.ports.file_loader import IFileLoader

class ICfnTemplateProvider(ABC):

    def __init__(self, file_loader_factory:Callable[[str], IFileLoader]) -> None:
        super().__init__()
        

    @abstractmethod
    def load_template(self) -> CfnTemplateDefinition:
        """load cfn template file(either json or yaml format) as dict"""

