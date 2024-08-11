# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os

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
    key_dict: dict[str, str] = {}

    try:
        key_dict["insee_key"] = os.environ["insee_key"]
        key_dict["insee_secret"] = os.environ["insee_secret"]

        envir_var_used = True
    except KeyError:
        envir_var_used = False

        config_file = os.path.join(
            user_config_dir("pynsee", ensure_exists=True), "config.json")

        try:
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
            logger.critical(
                "INSEE API credentials have not been found: please try to "
                "reuse pynsee.utils.init_conn to save them locally.\n"
                "Otherwise, you can still use environment variables as "
                "follow:\n"
                "import os\n"
                "os.environ['insee_key'] = 'my_insee_key'\n"
                "os.environ['insee_secret'] = 'my_insee_secret'"
            )

    if envir_var_used:
        logger.warning(
            "Existing environment variables used, instead of locally "
            "saved credentials"
        )

    return key_dict
