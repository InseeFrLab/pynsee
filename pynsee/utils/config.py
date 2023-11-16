# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
import urllib3

from typing import Any, Optional, Union

import platformdirs

from ._wait_api_query_limit import _wait_api_query_limit


logger = logging.getLogger(__name__)


_confdir = os.path.join(platformdirs.user_config_dir(), "pynsee")
_conf_file = os.path.join(_confdir, "config.json")


base_config: dict = {
    "http_proxy": None,
    "https_proxy": None,
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


def get_config(key: Optional[str] = None):
    '''
    Get pynsee configuration.

    Args:
        key (str, optional): specific configuration option to recover.
    '''
    if key in base_config:
        return base_config[key]
    elif key in _authorized:
        return None
    elif key is not None:
        raise KeyError(f"'{key}' is not in config.")

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
                # if credentials are provided, try to register a token
                from pynsee.utils.init_conn import _register_token

                token = None

                if "insee_secret" in config and "insee_key" in config:
                    # if both key and secret are provided, get token
                    import pynsee.utils._get_token_from_insee as gti

                    urllib3.disable_warnings(
                        urllib3.exceptions.InsecureRequestWarning)

                    key = config["insee_key"]

                    secret = config["insee_secret"]

                    token = gti._get_token_from_insee(key, secret)
                elif k == "insee_token":
                    # otherwise it's a token
                    token = config[k]
                else:
                    # or it's a mistake because we need either (key, secret)
                    # or the token, but not key alone or secret alone
                    logger.warning(
                        "Could not register a token from the given "
                        f"credential alone '{k}'. Please either provide "
                        "'insee_token' or 'insee_key' and 'insee_secret' "
                        "at the same time (in a dictionary).")

                if token and _register_token(token):
                    # ignore None or empty token
                    # an error will be raised if register is provided an
                    # invalid token
                    base_config["insee_token"] = token
                    register_token = False

            if k in _authorized:
                base_config[k] = v
            else:
                raise KeyError(f"Invalid option '{k}'.")
    except Exception as e:
        # there was an error, reset the config to its original state
        for k, v in original.items():
            base_config[k] = v

        raise e


def _register_token(
    token: str,
    http_proxy: Optional[str] = None,
    https_proxy: Optional[str] = None
) -> bool:
    '''
    Validate the token and register to INSEE APIs.
    Return True if the token is valid for all APIs.
    '''
    proxies = {
        "http": http_proxy or os.environ.get(
            "http_proxy", get_config("http_proxy")),
        "https": https_proxy or os.environ.get(
            "https_proxy", get_config("https_proxy"))
    }

    if not token:
        raise ValueError(
            "!!! Token is missing, please check that insee_key and "
            "insee_secret are correct !!!")
    else:
        headers = {
            "Accept": "application/xml",
            "Authorization": "Bearer " + (token or "")
        }

        url_test = "https://api.insee.fr/series/BDM/V1/data/CLIMAT-AFFAIRES"

        request_test = requests.get(
            url_test, proxies=proxies, headers=headers, verify=False)

        if request_test.status_code != 200:
            raise ValueError(f"This token is not working: {token}")

    queries = [
        "https://api.insee.fr/series/BDM/V1/dataflow/FR1/all",
        "https://api.insee.fr/metadonnees/V1/codes/cj/n3/5599",
        "https://api.insee.fr/entreprises/sirene/V3/siret?q=activitePrincipaleUniteLegale:86.10*&nombre=1000",
        "https://api.insee.fr/donnees-locales/V0.1/donnees/geo-SEXE-DIPL_19@GEO2020RP2017/FE-1.all.all",
    ]

    apis = ["BDM", "Metadata", "Sirene", "Local Data"]

    file_format = [
        "application/xml",
        "application/xml",
        "application/json;charset=utf-8",
        "application/xml",
    ]

    list_requests_status = []

    for q in range(len(queries)):
        headers = {
            "Accept": file_format[q],
            "Authorization": "Bearer " + token,
        }
        api_url = queries[q]

        _wait_api_query_limit(api_url)
        results = requests.get(
            api_url, proxies=proxies, headers=headers, verify=False
        )

        if results.status_code != 200:
            logger.critical(
                f"Please subscribe to {apis[q]} API on api.insee.fr !"
            )
        list_requests_status += [results.status_code]

    if all([sts == 200 for sts in list_requests_status]):
        return True

    return False


def _init_config_and_credentials():
    ''' Load the config file if it exists '''
    if os.path.isfile(_conf_file):
        with open(_conf_file, "r") as f:
            config = json.load(f)

            for k, v in config.items():
                base_config[k] = v
    else:
        os.makedirs(_confdir, exist_ok=True)

    # check environment variables for credentials
    envir_var_used = False

    insee_key = os.environ.get("insee_key", os.environ.get("INSEE_KEY"))

    insee_secret = os.environ.get(
        "insee_secret", os.environ.get("INSEE_SECRET"))

    if insee_key and insee_secret:
        set_config({"insee_key": insee_key, "insee_secret": insee_secret})
        envir_var_used = True
    else:
        token = os.environ.get("insee_token")

        if token:
            set_config("insee_token", token)
            envir_var_used = True

    if not get_config("insee_token"):
        logger.critical(
            "INSEE API credentials have not been found: please use "
            "pynsee.utils.init_conn to set them.\n"
            "Otherwise, you can use environment variables by setting:\n"
            "import os\n"
            "os.environ['insee_key'] = 'my_insee_key'\n"
            "os.environ['insee_secret'] = 'my_insee_secret'\n"
            "*before* the first line that imports pynsee."
        )
    elif envir_var_used:
        logger.warning(
            "Existing environment variables used, instead of locally "
            "saved credentials"
        )


_init_config_and_credentials()
