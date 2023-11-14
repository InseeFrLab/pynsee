# -*- coding: utf-8 -*-

import json
import logging
import os

from typing import Any, Optional, Union

import platformdirs

import pynsee
from pynsee.utils.init_conn import _register_token
from pynsee.utils._get_token import _get_token


logger = logging.getLogger(__name__)


_confdir = os.path.join(platformdirs.user_config_dir(), "pynsee")
_conf_file = os.path.join(_confdir, "config.json")


base_config: dict = {
    "http_proxy": "",
    "https_proxy": "",
    "hide_progress": False,
    "insee_key": None,
    "insee_secret": None,
    "insee_token": None,
}


_credentials = {"insee_key", "insee_secret", "insee_token"}


_authorized = set(
    list(base_config) + [
        "pynsee_file_list",
        "pynsee_use_sdmx",
        "pynsee_idbank_file",
    ]
)


def _load_config_file():
    ''' Load the config file if it exists '''
    if os.path.isfile(_conf_file):
        with open(_conf_file, "r") as f:
            config = json.load(f)

            for k, v in config.items():
                base_config[k] = v
    else:
        os.makedirs(_confdir, exist_ok=True)


def get_config(key: Optional[str] = None):
    '''
    Get pynsee configuration.

    Args:
        key (str, optional): specific configuration option to recover.
    '''
    if key:
        return base_config[key]

    return base_config.copy()


def save_config():
    ''' Save the config file '''
    with open(_conf_file, "w") as f:
        json.dump(base_config, f)


def set_config(config: Union[str, dict], value: Any = None):
    '''
    Set pynsee configuration.

    Args:
        config (str or dict): a dictionary to update the configuration or a
            the name of the configuration option that should be set to
            `value`.
        value (object): the new value for the `config` option.
    '''
    if not isinstance(config, dict):
        config = {config: value}

    # save original config in case there is an issue
    original = base_config.copy()

    register_token = True

    try:
        for k, v in config.items():
            if k in _credentials and register_token:
                key = config.get("insee_key", get_config("insee_key"))

                secret = config.get("insee_secret",
                                    get_config("insee_secret"))

                token = config.get("insee_token",
                                    get_config("insee_token"))

                if token is None:
                    token = _get_token(key, secret)

                if _register_token(token):
                    base_config["insee_token"] = token
                    register_token = False
                else:
                    cred = {"key": key, "secret": secret, "token": token}

                    raise RuntimeError(
                        "The provided credentials could not be validated "
                        f"{cred}.")

            if k in _authorized:
                base_config[k] = v
            else:
                raise KeyError(f"Invalid option '{k}'.")
    except Exception as e:
        for k, v in original.items():
            base_config[k] = v

        raise e


_load_config_file()
