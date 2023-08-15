from abc import ABC, abstractmethod
from typing import Optional

class IFileCache(ABC):

    def __init__(self, cache_root_dir:str) -> None:
        self.cache_root_dir = cache_root_dir

        super().__init__()

    @abstractmethod
    def put(self, filepath:str, body:str):
        pass
    @abstractmethod
    def get(self, filepath:str) -> Optional[str]:
        pass