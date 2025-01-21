# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import logging
import os

import requests

from platformdirs import user_config_dir

from pynsee.utils.requests_session import PynseeAPISession


logger = logging.getLogger(__name__)


def opener(path, flags):
    return os.open(path, flags, 0o600)


def init_conn(
    sirene_key: str = None, http_proxy: str = None, https_proxy: str = None
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
    """
    logger.debug("SHOULD GET LOGGING")

    queries = {
        "BDM": "https://api.insee.fr/series/BDM/dataflow/FR1/all",
        "Metadata": "https://api.insee.fr/metadonnees/codes/cj/n3/5599",
        "Sirene": "https://api.insee.fr/api-sirene/3.11/siret?q=activitePrincipaleUniteLegale:86.10*&nombre=1000",
        "Local Data": "https://api.insee.fr/donnees-locales/donnees/geo-SEXE-DIPL_19@GEO2020RP2017/FE-1.all.all",
    }
    invalid_requests = {}

    with PynseeAPISession(
        http_proxy=http_proxy, https_proxy=https_proxy, sirene_key=sirene_key
    ) as session:

        for api, api_url in queries.items():

            try:
                if api == "Sirene" and not session.sirene_key:
                    # the user is probably not expecting to use SIRENE anyway:
                    # simple warning and jump to next API in order to avoid
                    # urllib retries
                    logger.warning(
                        f"Remember to subscribe to {api} API on api.insee.fr "
                        "if you ever want to use it (type `help(init_conn)` "
                        "to know more about this)"
                    )
                    invalid_requests[api] = 999

                results = session.get(api_url, verify=False)
            except requests.exceptions.RequestException as exc:
                try:
                    exc.response.status_code
                except AttributeError:
                    raise RuntimeError(
                        f"Could not reach {api} at {api_url}, please control "
                        "your proxy configuration."
                    )
                if exc.response.status_code == 404:
                    raise RuntimeError(
                        f"Could not reach {api} at {api_url}, please get in "
                        "touch if the issue persists."
                    )
                elif results.status_code != 200:
                    logger.critical(
                        f"Please subscribe to {api} API on api.insee.fr !\n"
                        f"Received error {exc.response.status_code}: "
                    )

                invalid_requests[api] = exc.response.status_code

    config_file = os.path.join(
        user_config_dir("pynsee", ensure_exists=True), "config.json"
    )

    if invalid_requests:
        logger.error(
            "Invalid credentials, the following APIs returned error codes, "
            "please make sure you subscribed to them (if you need those):\n"
            f"{invalid_requests}"
        )
    elif len(invalid_requests) == len(queries):
        raise ValueError(
            "No API was reached. That's strange, please get in touch if the "
            "issue persists."
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
        "http_proxy": http_proxy if not http_proxy == "" else "DIRECT",
        "https_proxy": https_proxy if not https_proxy == "" else "DIRECT",
    }

    with open(config_file, "w", opener=opener) as f:
        json.dump(config, f)

    logger.info("Credentials have been saved.")
