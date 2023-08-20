from __future__ import annotations
from abc import ABC, abstractmethod

class IFileLoader(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def download(self, source:str) -> bytes:
        pass

    @abstractmethod
    def upload(self, body:bytes, dest:str) -> None:
        pass