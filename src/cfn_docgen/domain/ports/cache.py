from abc import ABC, abstractmethod
from typing import Optional

from cfn_docgen.config import AppContext

class IFileCache(ABC):

    def __init__(self, cache_root_dir:str, context:AppContext) -> None:
        self.cache_root_dir = cache_root_dir
        self.context = context

        super().__init__()

    @abstractmethod
    def put(self, filepath:str, body:str):
        pass
    @abstractmethod
    def get(self, filepath:str) -> Optional[str]:
        pass