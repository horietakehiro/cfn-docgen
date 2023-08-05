from __future__ import annotations
from abc import ABC, abstractmethod

DumpedJsonString = str

class IFileLoader(ABC):

    def __init__(self, filepath:str) -> None:
        self.filepath = filepath

    @abstractmethod
    def load(self) -> DumpedJsonString:
        """load data from given filepath and return it as json-convertible string"""