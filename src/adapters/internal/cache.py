import hashlib
import os
from config import AppConfig
from domain.ports.cache import IFileCache

HexHashString = str

class NoFileCache(IFileCache):

    def __init__(self, config: AppConfig) -> None:
        super().__init__(config)

    def get(self, filepath: str) -> str | None:
        return None
    
    def put(self, filepath: str, body: str):
        pass

class LocalFileCache(IFileCache):

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.cache_root_dir = os.path.join(
            self.config.APP_ROOT_DIR, "cache"
        )
        os.makedirs(self.cache_root_dir, exist_ok=True)

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
            with open(cache_filepath, "r", encoding=self.encoding) as fp:
                body = fp.read()
            return body
        return None