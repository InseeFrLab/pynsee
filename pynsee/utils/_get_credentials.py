# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os

from functools import lru_cache
from typing import Dict

from platformdirs import user_config_dir


logger = logging.getLogger(__name__)


def _get_credentials() -> Dict[str, str]:
    '''
    Try to load credentials.

    If the environment variables `insee_key` and `insee_secret` are set, use
    these.
    Otherwise try to load them from the config file.

    Returns a dict containing at least an "insee_key" and an "insee_secret"
    entry.
    '''
    key_dict: Dict[str, str] = {}

    sirene_key = os.environ.get("sirene_key")
    
    if sirene_key is None:
        sirene_key = os.environ.get("SIRENE_KEY")

    if sirene_key is None:
        envir_var_used = False
        try:
            config_file = os.path.join(
                user_config_dir("pynsee", ensure_exists=True), "config.json")
            
            with open(config_file, "r") as f:
                key_dict = json.load(f)
    
            http_proxy = key_dict["http_proxy"]
            https_proxy = key_dict["https_proxy"]
    
            if (http_proxy is None) or (not isinstance(http_proxy, str)):
                http_proxy = ""
            if (https_proxy is None) or (not isinstance(https_proxy, str)):
                https_proxy = ""
    
            os.environ["http_proxy"] = http_proxy
            os.environ["https_proxy"] = https_proxy
        except Exception:
            _missing_credentials()
    else:
        envir_var_used = True
        key_dict["sirene_key"] = sirene_key

    if envir_var_used:
        _warn_env_credentials()

    return key_dict


@lru_cache(maxsize=None)
def _missing_credentials() -> None:
    logger.critical(
        "INSEE API credentials have not been found: please try to reuse "
        "pynsee.utils.init_conn to save them locally.\n"
        "Otherwise, you can still use environment variables as follow:\n\n"
        "import os\n"
        "os.environ['sirene_key'] = 'my_sirene_key'"
    )


@lru_cache(maxsize=None)
def _warn_env_credentials() -> None:
    logger.warning(
        "Existing environment variables used, instead of locally "
        "saved credentials"
    )
