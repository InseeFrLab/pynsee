# -*- coding: utf-8 -*-

from typing import Any, Optional, Union

import pynsee


_authorized = set(
    list(pynsee._config) + [
        "pynsee_file_list",
        "pynsee_use_sdmx",
        "pynsee_idbank_file",
    ]
)


def get_config(key: Optional[str] = None):
    '''
    Get pynsee configuration.

    Args:
        key (str, optional): specific configuration option to recover.
    '''
    if key:
        return pynsee._config[key]

    return pynsee._config.copy()


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

    for k, v in config.items():
        if k in _authorized:
            pynsee._config[k] = v
        else:
            raise KeyError(f"Invalid option '{k}'.")
