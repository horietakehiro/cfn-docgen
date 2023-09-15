import glob
import os
from typing import List, Optional
from urllib.parse import urlparse
import requests
import boto3
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_document_generator import CfnDocumentDestination
from cfn_docgen.domain.model.cfn_template import CfnTemplateSource # type: ignore
from cfn_docgen.domain.ports.internal.file_loader import IFileLoader

def document_loader_factory(
    document_dest:CfnDocumentDestination,
    context:AppContext,
) -> IFileLoader:
    match document_dest.type:
        case "LocalFilePath":
            context.log_debug(f"document dest type is [{document_dest.type}]. return LocalFileLoader")
            return LocalFileLoader(context)
        case "S3BucketKey":
            context.log_debug(f"document dest type is [{document_dest.type}]. return S3FileLoader")
            return S3FileLoader(context)
        case "HttpUrl":
            context.log_debug(f"document dest type is [{document_dest.type}]. return RemoteFileLoader")
            return RemoteFileLoader(context)
        case _: # type: ignore
            raise NotImplementedError(f"document dest type [{document_dest.type}] is not supported")


def template_loader_factory(
    template_source:CfnTemplateSource,
    context:AppContext,
) -> IFileLoader:
    match template_source.type:
        case "LocalFilePath":
            context.log_debug(f"template source type is [{template_source.type}]. return LocalFileLoader")
            return LocalFileLoader(context)
        case "S3BucketKey":
            context.log_debug(f"template source type is [{template_source.type}]. return S3FileLoader")
            return S3FileLoader(context)
        case "HttpUrl":
            context.log_debug(f"template source type is [{template_source.type}]. return RemoteFileLoader")
            return RemoteFileLoader(context)
        case _: # type: ignore
            raise NotImplementedError(f"template source type [{template_source.type}] is not supported")

def specification_loader_factory(
    specification_url:str,
    context:AppContext
) -> IFileLoader:
    if specification_url.startswith("https://") or specification_url.startswith("http://"):
        context.log_debug("resource specification type is [http]. return RemoteFileLoader")
        return RemoteFileLoader(context)
    if specification_url.startswith("s3://"):
        context.log_debug("resource specification type is [s3]. return S3FileLoader")
        return S3FileLoader(context)
    
    context.log_debug("resource specification type is [local]. return LocalFileLoader")
    return LocalFileLoader(context)

class LocalFileLoader(IFileLoader):
    def __init__(self, context: AppContext) -> None:
        super().__init__(context)

    def download(self, source: str) -> bytes:
        with open(source, "rb") as fp:
            raw = fp.read()
        self.context.log_debug(f"download from [{source}]")
        return raw
    
    def upload(self, body: bytes, dest: str) -> None:
        # meke suer directory is exist
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fp:
            fp.write(body)
        self.context.log_debug(f"upload to [{dest}]")

    def list(self, source: str) -> List[str]:
        if os.path.isfile(source):
            self.context.log_debug(f"[{source}] is a single file")
            return [source]
        else:
            files_and_dir = glob.glob(os.path.join(source, "**"), recursive=True)
            self.context.log_debug(f"[{source}] is a directory. listed files are [{'.'.join(files_and_dir)}]")
            return sorted([f for f in files_and_dir if os.path.isfile(f)])

class RemoteFileLoader(IFileLoader):

    def __init__(self, context: AppContext) -> None:
        super().__init__(context)

    def download(self, source: str) -> bytes:
        res = requests.get(source, timeout=10)
        self.context.log_debug(f"download from [{source}]")
        return res.content

    def upload(self, body: bytes, dest: str) -> None:
        raise NotImplementedError
    
    def list(self, source: str) -> List[str]:
        raise NotImplementedError
    
class S3FileLoader(IFileLoader):
    def __init__(self, context: AppContext) -> None:
        super().__init__(context)
        self.client = boto3.client("s3") # type: ignore
        if context.connection_settings is not None:
            if context.connection_settings.aws.profile_name is not None:
                sess = boto3.Session(
                    profile_name=context.connection_settings.aws.profile_name
                )
                self.client = sess.client("s3") # type: ignore

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
        self.context.log_debug(f"download from [{source}]")
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
        self.context.log_debug(f"upload to [{dest}]")

    def list(self, source: str) -> List[str]:
        sources:List[str] = []

        source_url = urlparse(source)
        bucket = source_url.netloc
        prefix_or_key = source_url.path
        if prefix_or_key.startswith("/"):
            prefix_or_key = prefix_or_key[1:]

        # if source is a object key, return it
        try:
            res = self.client.head_object(
                Bucket=bucket,
                Key=prefix_or_key
            )
            self.context.log_debug(f"[{source}] is a single object")
            return [source]
        except Exception as ex:
            if "404" in str(ex):
                pass
            else:
                raise ex

        # if source is a prefix, return all keys
        prefix = prefix_or_key
        if not prefix.endswith("/"):
            prefix += "/"
        res = self.client.list_objects_v2(
            Bucket=bucket, Prefix=prefix
        )
        contents = res.get("Contents", None)
        if contents is None: # type: ignore
            return sources
        for content in contents:
            sources.append(
                os.path.join(f"s3://{bucket}",  content["Key"]) # type: ignore
            )
        next_token:Optional[str] = res.get("NextContinuationToken", None)
        while next_token is not None: # type: ignore
            res = self.client.list_objects_v2(
                Bucket=bucket, Prefix=prefix,
                ContinuationToken=next_token,
            )
            contents = res.get("Contents", None)
            if contents is None: # type: ignore
                return sources
            for content in contents:
                sources.append(
                    os.path.join(f"s3://{bucket}", content["Key"]) # type: ignore
                )
            next_token:str|None = res.get("NextContinuationToken", None)

        self.context.log_debug(f"[{source}] is a directory. listed keys are [{'.'.join(sources)}]")
        return sources