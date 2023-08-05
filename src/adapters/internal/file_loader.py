import requests
from cfn_flip import to_json # type: ignore

from src.domain.ports.file_loader import DumpedJsonString, IFileLoader

def get_file_loader(filepath:str) -> IFileLoader:
    """return proper file loader instance for the given filepath"""
    if filepath.startswith("https://"):
        return RemoteFileLoader(filepath)
    
    return LocalFileLoader(filepath)


class LocalFileLoader(IFileLoader):
    """load cfn template file in local filepath"""
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def load(self) -> DumpedJsonString:
        """load cfn template file and return as json-convertible string"""
        with open(self.filepath, "r", encoding="UTF-8") as fp:
            raw = fp.read()
        if raw.startswith("{") and raw.endswith("}"):
            return raw
        return to_json(raw)

class RemoteFileLoader(IFileLoader):
    """load cfn specification file from remote server"""
    def __init__(self, filepath: str) -> None:
        assert (
            filepath.startswith("https://")
        ), "filepath must be a form of https url (e.g. https://example.com/file.json)"
        self.filepath = filepath

    def load(self) -> DumpedJsonString:
        """download remote file and return as json-convertible string"""
        res = requests.get(self.filepath, timeout=10)
        return res.content.decode(encoding="utf-8")
