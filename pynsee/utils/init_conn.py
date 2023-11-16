# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import logging
import urllib3

from typing import Optional

from .config import (
    _conf_file, _register_token, get_config, set_config, save_config)
from ._get_token_from_insee import _get_token_from_insee


logger = logging.getLogger(__name__)


def init_conn(
    insee_key: str,
    insee_secret: str,
    http_proxy: Optional[str] = None,
    https_proxy: Optional[str] = None
) -> None:
    """Save your credentials to connect to INSEE APIs, subscribe to api.insee.fr

    Args:
        insee_key (str): user's key
        insee_secret (str): user's secret
        http_proxy (str, optional): Proxy server address, e.g. 'http://my_proxy_server:port'. Defaults to "".
        https_proxy (str, optional): Proxy server address, e.g. 'http://my_proxy_server:port'. Defaults to "".

    Notes:
        Environment variables can be used instead of init_conn function

    Examples:
        >>> from pynsee.utils.init_conn import init_conn
        >>> init_conn(insee_key="my_insee_key", insee_secret="my_insee_secret")
        >>> #
        >>> # if the user has to use a proxy server use http_proxy and https_proxy arguments as follows:
        >>> from pynsee.utils.init_conn import init_conn
        >>> init_conn(insee_key="my_insee_key",
        >>>           insee_secret="my_insee_secret",
        >>>           http_proxy="http://my_proxy_server:port",
        >>>           https_proxy="http://my_proxy_server:port")
        >>> #
        >>> # Alternativety you can use directly environment variables as follows:
        >>> # Beware not to commit your credentials!
        >>> import os
        >>> os.environ['insee_key'] = 'my_insee_key'
        >>> os.environ['insee_secret'] = 'my_insee_secret'
        >>> os.environ['http_proxy'] = "http://my_proxy_server:port"
        >>> os.environ['https_proxy'] = "http://my_proxy_server:port"
    """
    logger.debug("SHOULD GET LOGGING")

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    token = _get_token_from_insee(insee_key, insee_secret)

    if _register_token(token, http_proxy, https_proxy):
        config = {
            "insee_key": insee_key,
            "insee_secret": insee_secret,
            "insee_token": token
        }

        set_config(config)

        save_config()

        logger.warning(
            "Subscription to all INSEE's APIs has been successfull\n"
            "Unless the user wants to change key or secret, using this "
            "function is no longer needed as the credentials to get the token "
            "have been saved locally here:\n" + _conf_file
        )
