import hashlib
import os
from cfn_docgen.config import AppContext
from cfn_docgen.domain.ports.cache import IFileCache

HexHashString = str

class NoFileCache(IFileCache):

    def __init__(self, cache_root_dir: str, context: AppContext) -> None:
        super().__init__(cache_root_dir, context)
        
    def get(self, filepath: str) -> str | None:
        return None
    
    def put(self, filepath: str, body: str):
        pass

class LocalFileCache(IFileCache):

    def __init__(self, cache_root_dir: str, context: AppContext) -> None:
        super().__init__(cache_root_dir, context)
        os.makedirs(self.cache_root_dir, exist_ok=True)
        context.log_debug(f"create directory for cache at [{self.cache_root_dir}]")

        self.encoding = "UTF-8"

    def hash(self, string:str) -> HexHashString:
        h = hashlib.md5(string.encode())
        return h.hexdigest()
    
    def put(self, filepath: str, body: str):
        filepath_hash = self.hash(filepath)
        cache_filepath = os.path.join(self.cache_root_dir, filepath_hash)
        with open(cache_filepath, "w", encoding=self.encoding) as fp:
            fp.write(body)

    def get(self, filepath: str) -> str | None:
        filepath_hash = self.hash(filepath)
        cache_filepath = os.path.join(self.cache_root_dir, filepath_hash)
        if os.path.isfile(cache_filepath):
            self.context.log_debug(f"cache [{cache_filepath}] hit")
            with open(cache_filepath, "r", encoding=self.encoding) as fp:
                body = fp.read()
            return body
        return None