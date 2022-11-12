import shutil
import os
from logging import Handler, Logger, getLogger, Formatter, StreamHandler, FileHandler, DEBUG, INFO

APP_BASE_DIR=os.path.join(os.environ.get("HOME", os.environ.get("HOMEPATH")), ".cfn-docgen")
CACHE_BASE_DIR=os.path.join(APP_BASE_DIR, "cache")
LOG_BASE_DIR=os.path.join(APP_BASE_DIR, "log")
os.makedirs(CACHE_BASE_DIR, exist_ok=True)
os.makedirs(LOG_BASE_DIR, exist_ok=True)

def remove_cache():
    shutil.rmtree(CACHE_BASE_DIR)

def get_verbose():
    verbose = os.environ.get("CFN_DOCGEN_VERBOSE", "FALSE")
    return verbose == "TRUE"

def get_module_logger(module:str, verbose:bool) -> Logger:
    logger = getLogger(module)
    logger = _set_handler(logger, StreamHandler(), verbose)
    logger = _set_handler(logger, FileHandler(os.path.join(LOG_BASE_DIR, "cfn-docgen.log"), mode="w+"), True)
    logger.setLevel(DEBUG)
    logger.propagate = False
    return logger

def _set_handler(logger:Logger, handler:Handler, verbose:bool) -> Logger:
    if verbose:
        handler.setLevel(DEBUG)
    else:
        handler.setLevel(INFO)
    handler.setFormatter(Formatter('%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s'))
    logger.addHandler(handler)
    return logger