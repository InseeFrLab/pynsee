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
    """
    Try to load credentials.

    If the environment variable `sirene_key` is set, use it.
    Otherwise try to load it from the config file.

    Returns a dict containing at least an "sirene_key" entry.
    """
    key_dict: Dict[str, str] = {}

    def get_env_case_insensitive(x: str):
        "Fetch an environment variable (case insentitive)"
        val = os.environ.get(x)
        if val is None:
            return os.environ.get(x.upper())
        return val

    sirene_key = get_env_case_insensitive("sirene_key")
    http_proxy = get_env_case_insensitive("http_proxy")
    https_proxy = get_env_case_insensitive("https_proxy")

    if sirene_key == "":
        envir_var_used = False
        try:
            config_file = os.path.join(
                user_config_dir("pynsee", ensure_exists=True), "config.json"
            )

            with open(config_file, "r") as f:
                key_dict = json.load(f)

            if key_dict["http_proxy"] != http_proxy:
                logger.warning(
                    f"Current http_proxy ({http_proxy}) is being overwritten "
                    "by pynsee config. "
                    "To reset it, please use pynsee.utils.init_conn.\n"
                    f"Used http_proxy is now {key_dict['http_proxy']}"
                )
                http_proxy = key_dict["http_proxy"]

            if key_dict["https_proxy"] != https_proxy:
                logger.warning(
                    f"Current https_proxy ({http_proxy}) is being overwritten "
                    "by pynsee config. "
                    "To reset it, please use pynsee.utils.init_conn.\n"
                    f"Used http_proxy is now {key_dict['http_proxy']}"
                )
                https_proxy = key_dict["https_proxy"]

            if not isinstance(http_proxy, str):
                http_proxy = ""

            if not isinstance(https_proxy, str):
                https_proxy = ""

            key_dict["https_proxy"] = https_proxy
            key_dict["http_proxy"] = https_proxy

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
