import requests
from domain.model.cfn_document_generator import CfnDocumentDestination
from domain.model.cfn_template import CfnTemplateSource # type: ignore

from domain.ports.internal.file_loader import IFileLoader

def document_loader_factory(document_dest:CfnDocumentDestination) -> IFileLoader:
    match document_dest.type:
        case "LocalFilePath":
            return LocalFileLoader()
        case _: # type: ignore
            raise NotImplementedError()

def file_loader_factory(template_source:CfnTemplateSource) -> IFileLoader:
    match template_source.type:
        case "LocalFilePath":
            return LocalFileLoader()
        
        case _: # type: ignore
            raise NotImplementedError()


class LocalFileLoader(IFileLoader):
    def __init__(self) -> None:
        super().__init__()

    def download(self, source: str) -> bytes:
        with open(source, "rb") as fp:
            raw = fp.read()
        return raw
    
    def upload(self, body: bytes, dest: str) -> None:
        with open(dest, "wb") as fp:
            fp.write(body)

class RemoteFileLoader(IFileLoader):
    def __init__(self) -> None:
        super().__init__()

    def download(self, source: str) -> bytes:
        res = requests.get(source, timeout=10)
        return res.content

    def upload(self, body: bytes, dest: str) -> None:
        raise NotImplementedError