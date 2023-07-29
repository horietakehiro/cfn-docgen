from abc import ABC, abstractmethod


class IFileLoader(ABC):

    def __init__(self, filepath:str) -> None:
        super().__init__()

    @abstractmethod
    def load(self) -> str:
        """load data from given filepath and return it as string"""