from abc import ABC, abstractmethod

class ILogger(ABC):

    def __init__(self, name:str, level:int) -> None:
        super().__init__()

    @abstractmethod
    def info(self, msg:str):
        pass
    @abstractmethod
    def warning(self, msg:str):
        pass
    @abstractmethod
    def error(self, msg:str):
        pass
    @abstractmethod
    def debug(self, msg:str):
        pass