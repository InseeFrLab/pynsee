# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os

from functools import lru_cache
from typing import Dict

from platformdirs import user_config_dir


logger = logging.getLogger(__name__)


def _get_credentials_from_configfile() -> Dict[str, str]:
    """
    Try to load credentials and proxy configuration from config file.

    Returns a dict containing at least an "sirene_key" entry.
    """
    key_dict: Dict[str, str] = {}

    config_file = os.path.join(
        user_config_dir("pynsee", ensure_exists=True), "config.json"
    )

    try:
        with open(config_file, "r") as f:
            key_dict = json.load(f)

    except FileNotFoundError:
        # no credentials/config stored
        _missing_credentials()
        return key_dict

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
