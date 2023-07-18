# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import logging
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

import pynsee


logger = logging.getLogger(__name__)


def _get_credentials():
    ''' Store INSEE credentials into pynsee configuration dict '''
    if not pynsee._config["insee_key"]:
        envir_var_used = False

        try:
            home = str(Path.home())
            pynsee_credentials_file = home + "/" + "pynsee_credentials.csv"
            cred = pd.read_csv(pynsee_credentials_file)

            pynsee._config["insee_key"] = str(cred.loc[0, "insee_key"])
            pynsee._config["insee_secret"] = str(cred.loc[0, "insee_secret"])

            try:
                http_proxy = cred.loc[0, "http_proxy"]
                https_proxy = cred.loc[0, "https_proxy"]

                if http_proxy:
                    pynsee._config["http_proxy"] = http_proxy
                if https_proxy:
                    pynsee._config["https_proxy"] = https_proxy
            except KeyError:
                pass
        except Exception as e:
            logging.warning(f"Failed to retrieve credentials from file: {e}.")
            envir_var_used = True

        try:
            pynsee._config["insee_key"] = os.environ["insee_key"]
            pynsee._config["insee_secret"] = os.environ["insee_secret"]
        except Exception:
            try:
                pynsee._config["insee_key"] = os.environ["INSEE_KEY"]
                pynsee._config["insee_secret"] = os.environ["INSEE_SECRET"]
            except KeyError:
                pass

        if not pynsee._config["insee_key"]:
            _warning_credentials("key_dict_none")
        elif envir_var_used:
            _warning_credentials("envir_var_used")
        else:
            logger.info("Token has been created")


@lru_cache(maxsize=None)
def _warning_credentials(string):
    if string == "envir_var_used":
        logger.warning(
            "Existing environment variables used, instead of locally "
            "saved credentials"
        )
    if string == "key_dict_none":
        logger.critical(
            "INSEE API credentials have not been found: please try to reuse "
            "pynsee.utils.init_conn to save them locally.\n"
            "Otherwise, you can still use environment variables as follow:\n"
            "import os\n"
            "os.environ['insee_key'] = 'my_insee_key'\n"
            "os.environ['insee_secret'] = 'my_insee_secret'"
        )
