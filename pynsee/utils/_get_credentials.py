# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pathlib import Path
import os
import pandas as pd
from functools import lru_cache
import numpy as np


def _get_credentials():

    envir_var_used = False
    try:
        home = str(Path.home())
        pynsee_credentials_file = home + "/" + "pynsee_credentials.csv"
        cred = pd.read_csv(pynsee_credentials_file)
        os.environ["insee_key"] = str(cred.loc[0, "insee_key"])
        os.environ["insee_secret"] = str(cred.loc[0, "insee_secret"])
        proxy_server = cred.loc[0, "proxy_server"]
        if (proxy_server is None) or (np.isnan(proxy_server)):
            proxy_server = ""
        os.environ["http_proxy"] = str(proxy_server)
        os.environ["https_proxy"] = str(proxy_server)
    except:
        envir_var_used = True

    try:
        key_dict = {
            "insee_key": os.environ["insee_key"],
            "insee_secret": os.environ["insee_secret"],
        }
    except:
        try:
            key_dict = {
                "insee_key": os.environ["INSEE_KEY"],
                "insee_secret": os.environ["INSEE_SECRET"],
            }
        except:
            key_dict = None

    if (envir_var_used is True) & (key_dict is not None):
        _warning_credentials("envir_var_used")
    elif key_dict is None:
        _warning_credentials("key_dict_none")

    return key_dict


@lru_cache(maxsize=None)
def _warning_credentials(string):
    if string == "envir_var_used":
        print(
            "!!! Existing environment variables used, instead of locally saved credentials !!!"
        )
    if string == "key_dict_none":
        print("INSEE API credentials have not been found")
        print("Please try to reuse pynsee.utils.init_conn to save them locally")
        print("Otherwise, you can still use environment variables as follow:")
        print("import os")
        print("os.environ['insee_key'] = 'my_insee_key'")
        print("os.environ['insee_secret'] = 'my_insee_secret'")
