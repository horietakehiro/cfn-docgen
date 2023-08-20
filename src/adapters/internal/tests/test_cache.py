
import os
from adapters.internal.cache import LocalFileCache

from config import AppConfig


def test_LocalFileCache_put():
    path1 = "/foo/bar.json"
    body1 = "foobar"
    cache = LocalFileCache(AppConfig.CACHE_ROOT_DIR)

    cache.put(path1, body1)
    cache_filepath = os.path.join(
        cache.cache_root_dir, cache.hash(path1)
    )
    assert os.path.isfile(cache_filepath), f"{cache_filepath} does not exists"
    with open(cache_filepath, "r", encoding=cache.encoding) as fp:
        assert body1 == fp.read()


def test_LocalFileCache_get():
    path1 = "/foo/bar.json"
    body1 = "foobar"
    cache = LocalFileCache(AppConfig.CACHE_ROOT_DIR)
    
    cache.put(path1, body1)

    assert body1 == cache.get(path1)
    assert cache.get("not-exist") is None


