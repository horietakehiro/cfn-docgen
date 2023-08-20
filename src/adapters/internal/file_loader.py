from urllib.parse import urlparse
import requests
import boto3
from domain.model.cfn_document_generator import CfnDocumentDestination
from domain.model.cfn_template import CfnTemplateSource # type: ignore

from domain.ports.internal.file_loader import IFileLoader

def document_loader_factory(document_dest:CfnDocumentDestination) -> IFileLoader:
    match document_dest.type:
        case "LocalFilePath":
            return LocalFileLoader()
        case "S3BucketKey":
            return S3FileLoader()
        case "HttpUrl":
            return RemoteFileLoader()
        case _: # type: ignore
            raise NotImplementedError()

def file_loader_factory(template_source:CfnTemplateSource) -> IFileLoader:
    match template_source.type:
        case "LocalFilePath":
            return LocalFileLoader()
        case "S3BucketKey":
            return S3FileLoader()
        case "HttpUrl":
            return RemoteFileLoader()
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
    
class S3FileLoader(IFileLoader):
    def __init__(self) -> None:
        self.client = boto3.client("s3") # type: ignore
        super().__init__()
    def download(self, source: str) -> bytes:
        s3_url = urlparse(source)
        bucket = s3_url.netloc
        key = s3_url.path
        if key.startswith("/"):
            key = key[1:]
        res = self.client.get_object(
            Bucket=bucket,
            Key=key,
        )
        return res["Body"].read()
    
    def upload(self, body: bytes, dest: str) -> None:
        s3_url = urlparse(dest)
        bucket = s3_url.netloc
        key = s3_url.path
        if key.startswith("/"):
            key = key[1:]
        self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
        )