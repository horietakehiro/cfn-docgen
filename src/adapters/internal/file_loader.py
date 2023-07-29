from cfn_flip import to_json # type: ignore

from src.domain.ports.file_loader import IFileLoader

def get_file_loader(filepath:str) -> IFileLoader:
    """return proper file loader instance for the given filepath"""
    return LocalFileLoader(filepath)


class LocalFileLoader(IFileLoader):
    """load cfn template file in local filepath"""
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def load(self) -> str:
        """load cfn template file and return as json-convertible string"""
        with open(self.filepath, "r", encoding="UTF-8") as fp:
            raw = fp.read()
        if raw.startswith("{") and raw.endswith("}"):
            return raw
        return to_json(raw)
