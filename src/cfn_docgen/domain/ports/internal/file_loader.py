from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from cfn_docgen.config import AppContext

class IFileLoader(ABC):

    def __init__(self, context:AppContext) -> None:
        self.context = context

    @abstractmethod
    def download(self, source:str) -> bytes:
        pass

    @abstractmethod
    def upload(self, body:bytes, dest:str) -> None:
        pass

    @abstractmethod
    def list(self, source:str) -> List[str]:
        pass