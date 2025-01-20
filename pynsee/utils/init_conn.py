# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os
import requests
import time

from platformdirs import user_config_dir

from pynsee.utils.requests_params import (
    _get_requests_session,
    _get_requests_headers,
    _get_requests_proxies,
)


logger = logging.getLogger(__name__)


def opener(path, flags):
    return os.open(path, flags, 0o600)


def init_conn(
    sirene_key: str, http_proxy: str = "", https_proxy: str = ""
) -> None:
    """Save your credentials to connect to INSEE APIs, subscribe to api.insee.fr

    Args:
        sirene_key (str): user's key for sirene API
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
    """
    logger.debug("SHOULD GET LOGGING")

    proxies = _get_requests_proxies()

    queries = {
        "BDM": "https://api.insee.fr/series/BDM/V1/dataflow/FR1/all",
        "Metadata": "https://api.insee.fr/metadonnees/V1/codes/cj/n3/5599",
        "Sirene": "https://api.insee.fr/api-sirene/3.11/siret?q=activitePrincipaleUniteLegale:86.10*&nombre=1000",
        "Local Data": "https://api.insee.fr/donnees-locales/V0.1/donnees/geo-SEXE-DIPL_19@GEO2020RP2017/FE-1.all.all",
    }

    file_format = {
        "BDM": "application/xml",
        "Metadata": "application/xml",
        "Sirene": "application/json;charset=utf-8",
        "Local Data": "application/xml",
    }

    invalid_requests = {}

    user_agent = _get_requests_headers()

    session = _get_requests_session()

    for api, api_url in queries.items():
        headers = {
            "Accept": file_format[api],
            "User-Agent": user_agent["User-Agent"],
        }
        if api == "Sirene":
            headers["X-INSEE-Api-Key-Integration"] = sirene_key

        results = session.get(
            api_url, proxies=proxies, headers=headers, verify=False
        )

        code = results.status_code

        if code == 429:
            time.sleep(10)

            results = requests.get(
                api_url, proxies=proxies, headers=headers, verify=False
            )

        if results.status_code == 404:
            RuntimeError(
                f"Could not reach {api} at {api_url}, please get in touch if "
                "the issue persists."
            )
        elif results.status_code != 200:
            logger.critical(
                f"Please subscribe to {api} API on api.insee.fr !\n"
                f"Received error {results.status_code}: "
            )

            invalid_requests[api] = results.status_code

    session.close()

    config_file = os.path.join(
        user_config_dir("pynsee", ensure_exists=True), "config.json"
    )

    if invalid_requests:
        raise ValueError(
            "Invalid credentials, the following APIs returned error codes, "
            "please make sure you subscribed to them:\n"
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
    config = {
        "sirene_key": sirene_key,
        "http_proxy": http_proxy,
        "https_proxy": https_proxy,
    }

    with open(config_file, "w", opener=opener) as f:
        json.dump(config, f)

    logger.info("Credentials have been saved.")
