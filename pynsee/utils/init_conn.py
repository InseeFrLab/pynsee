# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os
from typing import Optional

from platformdirs import user_config_dir
import requests

from pynsee.utils.requests_session import PynseeAPISession


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
        >>> from pynsee.utils.init_conn import init_conn
        >>> init_conn(sirene_key="my_sirene_key")
        >>> #
        >>> # if the user has to use a proxy server use http_proxy and https_proxy arguments as follows:
        >>> from pynsee.utils.init_conn import init_conn
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

    config_file = os.path.join(
        user_config_dir("pynsee", ensure_exists=True), "config.json"
    )

    with PynseeAPISession(
        sirene_key=sirene_key, http_proxy=http_proxy, https_proxy=https_proxy
    ) as session:
        try:
            invalid_requests = session._test_connections()
        except (ValueError, requests.exceptions.RequestException):
            try:
                os.unlink(config_file)
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
            f"locally here:\n{config_file}"
        )

    # save config
    if not invalid_requests and ("Sirene" not in invalid_requests):
        # everything works, or at least SIRENE
        config = {
            "sirene_key": sirene_key,
            "http_proxy": http_proxy,
            "https_proxy": https_proxy,
        }

        with open(config_file, "w", opener=opener, encoding="utf8") as f:
            json.dump(config, f)

        logger.info("Credentials have been saved.")

    elif invalid_requests:
        # some APIs are working, excepting SIRENE. User has already been warned
        # about this.
        config = {
            "sirene_key": None,
            "http_proxy": http_proxy,
            "https_proxy": https_proxy,
        }

    with open(config_file, "w", opener=opener, encoding="utf8") as f:
        json.dump(config, f)

    logger.info("Credentials have been saved.")
