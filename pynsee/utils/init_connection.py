# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os
from typing import Optional

import requests

from pynsee.utils.requests_session import PynseeAPISession
from pynsee.constants import (
    CONFIG_FILE,
    SIRENE_KEY,
    HTTPS_PROXY_KEY,
    HTTP_PROXY_KEY,
)


logger = logging.getLogger(__name__)


def opener(path, flags):
    return os.open(path, flags, 0o600)


def init_conn(
    sirene_key: Optional[str] = None,
    http_proxy: Optional[str] = None,
    https_proxy: Optional[str] = None,
) -> None:
    """Save your credentials to connect to INSEE APIs, subscribe to api.insee.fr

    Args:
        sirene_key (str, optional): user's key for sirene API
        http_proxy (str, optional): Proxy server address, e.g. 'http://my_proxy_server:port'. Defaults to "".
        https_proxy (str, optional): Proxy server address, e.g. 'http://my_proxy_server:port'. Defaults to "".

    Notes:
        Environment variables can be used instead of init_conn function

    Examples:
        >>> from pynsee.utils import init_conn
        >>> init_conn(sirene_key="my_sirene_key")
        >>> #
        >>> # if the user has to use a proxy server use http_proxy and https_proxy arguments as follows:
        >>> from pynsee.utils import init_conn
        >>> init_conn(sirene_key="my_sirene_key",
        >>>           http_proxy="http://my_proxy_server:port",
        >>>           https_proxy="http://my_proxy_server:port")
        >>> #
        >>> # Alternativety you can use directly environment variables as follows:
        >>> # Beware not to commit your credentials!
        >>> import os
        >>> os.environ['sirene_key'] = 'my_sirene_key'
        >>> os.environ['http_proxy'] = "http://my_proxy_server:port"
        >>> os.environ['https_proxy'] = "http://my_proxy_server:port"
        >>> init_conn()
    """
    logger.debug("SHOULD GET LOGGING")

    try:
        with open(CONFIG_FILE, opener=opener, encoding="utf8") as f:
            init_config = json.load(f)
    except FileNotFoundError:
        init_config = {}

    with PynseeAPISession(
        sirene_key=sirene_key, http_proxy=http_proxy, https_proxy=https_proxy
    ) as session:
        try:
            invalid_requests = session._test_connections()
        except (ValueError, requests.exceptions.RequestException):
            try:
                os.remove(CONFIG_FILE)
            except FileNotFoundError:
                pass
            raise

    if invalid_requests:
        logger.error(
            "Invalid credentials, the following APIs returned error codes, "
            "please make sure you subscribed to them (if you need those):\n"
            f"{invalid_requests}"
        )
    else:
        logger.info(
            "Subscription to all INSEE's APIs has been successfull\n"
            "Unless the user wants to change the key or secret, using this "
            "function is no longer needed as the credentials will be saved "
            f"locally here:\n{CONFIG_FILE}"
        )

    if invalid_requests and ("Sirene" in invalid_requests):

        if not sirene_key:
            # user has probably no use for SIRENE API and has already
            # been warned about this
            sirene_key = None
        else:
            # invalid sirene key, restore from previous valid stored key
            try:
                sirene_key = init_config[SIRENE_KEY]
            except KeyError:
                sirene_key = None
            else:
                logger.warning("Previous SIRENE key has been restored.")

    config = {
        SIRENE_KEY: sirene_key,
        HTTP_PROXY_KEY: http_proxy,
        HTTPS_PROXY_KEY: https_proxy,
    }

    if {"Sirene"}.issuperset(invalid_requests):
        with open(CONFIG_FILE, "w", opener=opener, encoding="utf8") as f:
            json.dump(config, f)
        logger.info("Credentials have been saved.")
