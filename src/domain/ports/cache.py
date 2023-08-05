from abc import ABC, abstractmethod
from typing import Optional

from src.config import AppConfig


class IFileCache(ABC):

    def __init__(self, config:AppConfig) -> None:
        super().__init__()

    @abstractmethod
    def put(self, filepath:str, body:str):
        pass
    @abstractmethod
    def get(self, filepath:str) -> Optional[str]:
        pass