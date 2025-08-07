# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import re

from functools import lru_cache
from typing import Dict

from pynsee.constants import CONFIG_FILE


logger = logging.getLogger(__name__)


def _get_credentials_from_configfile(url) -> Dict[str, str]:
    """
    Try to load credentials and proxy configuration from config file.

    Returns a dict containing at least an "sirene_key" entry.
    """
    key_dict: Dict[str, str] = {}

    try:
        with open(CONFIG_FILE, "r") as f:
            key_dict = json.load(f)

    except FileNotFoundError:
        if re.match(".*api-sirene.*", url):
            # no credentials/config stored
            _missing_credentials()
        return key_dict

    return key_dict


@lru_cache(maxsize=None)
def _missing_credentials() -> None:
    logger.critical(
        "INSEE API credentials have not been found: please try to reuse "
        "pynsee.init_conn to save them locally.\n"
        "Otherwise, you can still use environment variables as follow:\n\n"
        "import os\n"
        "os.environ['sirene_key'] = 'my_sirene_key'"
    )
