
import logging
import os

import pytest
from cfn_docgen.adapters.internal.cache import LocalFileCache

from cfn_docgen.config import AppConfig, AppContext, AwsConnectionSettings, ConnectionSettings

@pytest.fixture
def context():
    return AppContext(
        log_level=logging.DEBUG, 
        connection_settings=ConnectionSettings(aws=AwsConnectionSettings(profile_name=None)),
    )

def test_LocalFileCache_put(context:AppContext):
    path1 = "/foo/bar.json"
    body1 = "foobar"
    cache = LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context)

    cache.put(path1, body1)
    cache_filepath = os.path.join(
        cache.cache_root_dir, cache.hash(path1)
    )
    assert os.path.isfile(cache_filepath), f"{cache_filepath} does not exists"
    with open(cache_filepath, "r", encoding=cache.encoding) as fp:
        assert body1 == fp.read()


def test_LocalFileCache_get(context:AppContext):
    path1 = "/foo/bar.json"
    body1 = "foobar"
    cache = LocalFileCache(AppConfig.CACHE_ROOT_DIR, context=context)
    
    cache.put(path1, body1)

    assert body1 == cache.get(path1)
    assert cache.get("not-exist") is None


