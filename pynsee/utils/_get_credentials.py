# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import logging
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

import pynsee
from pynsee.utils._get_token import _get_token


logger = logging.getLogger(__name__)


def _get_credentials():
    ''' Get INSEE credentials and return token '''
    envir_var_used = False

    try:
        pynsee.set_config("insee_key", os.environ["insee_key"])
        pynsee.set_config("insee_secret", os.environ["insee_secret"])
        envir_var_used = True
    except KeyError:
        try:
            pynsee.set_config("insee_key", os.environ["INSEE_KEY"])
            pynsee.set_config("insee_secret", os.environ["INSEE_SECRET"])
            envir_var_used = True
        except KeyError:
            pass

    if not pynsee.get_config("insee_key"):
        logger.critical(
            "INSEE API credentials have not been found: please try to reuse "
            "pynsee.utils.init_conn to save them locally.\n"
            "Otherwise, you can still use environment variables as follow:\n"
            "import os\n"
            "os.environ['insee_key'] = 'my_insee_key'\n"
            "os.environ['insee_secret'] = 'my_insee_secret'"
        )
    elif envir_var_used:
        logger.warning(
            "Existing environment variables used, instead of locally "
            "saved credentials"
        )
