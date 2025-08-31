# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging

from pynsee.constants import CONFIG_FILE


logger = logging.getLogger(__name__)


def _get_credentials_from_configfile() -> dict[str, str]:
    """
    Try to load credentials and proxy configuration from config file.

    Returns a dict containing at least an "sirene_key" entry.
    """
    key_dict: dict[str, str] = {}

    try:
        with open(CONFIG_FILE, "r") as f:
            key_dict = json.load(f)
    except FileNotFoundError:
        pass

    return key_dict
