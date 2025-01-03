# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
import requests
import urllib3
import time
import re

from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils.requests_params import (
    _get_requests_session,
    _get_requests_headers,
    _get_requests_proxies,
)
from pynsee.utils._wait_api_query_limit import _wait_api_query_limit

import logging

logger = logging.getLogger(__name__)

CODES = {
    # 200:"Opération réussie",
    # 301:"Moved Permanently" -> r.headers['location']
    400: "Bad Request",
    401: "Unauthorized : token missing",
    403: "Forbidden : missing subscription to API",  #
    404: "Not Found : no results available",
    406: "Not acceptable : incorrect 'Accept' header",
    413: "Too many results, query must be splitted",
    414: "Request-URI Too Long",
    # Unused (managed through a specific if/else), kept for memory purpose
    # 429: "Too Many Requests : allocated quota overloaded",
    500: "Internal Server Error ",
    503: "Service Unavailable",
}


def _request_insee(
    api_url=None, sdmx_url=None, file_format="application/xml", print_msg=True
):
    # sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
    # api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"
    # api_url = 'https://api.insee.fr/series/BDM/V1/data/CLIMAT-AFFAIRES/?firstNObservations=4&lastNObservations=1'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    keys = _get_credentials()

    if api_url is not None:
        logger.debug(api_url)
    elif sdmx_url is not None:
        logger.debug(sdmx_url)

    proxies = _get_requests_proxies()

    try:
        print_url = os.environ["pynsee_print_url"]
        if print_url == "True":
            print(api_url)
    except:
        pass

    # force sdmx use with a system variable
    try:
        pynsee_use_sdmx = os.environ["pynsee_use_sdmx"]
        if pynsee_use_sdmx == "True":
            api_url = None
    except:
        pass

    # if api_url is provided, it is used first,
    # and the sdmx url is used as a backup in two cases
    # 1- when the token is missing
    # 2- if the api request fails

    # if api url is missing sdmx url is used

    if api_url is not None:
        if keys is not None:
            try:
                sirene_key = keys["sirene_key"]
            except:
                sirene_key = None                
        else:
            sirene_key = None

        user_agent = _get_requests_headers()

        headers = {
            "Accept": file_format,
            "User-Agent": user_agent["User-Agent"],
        }

        session = _get_requests_session()

        sirene_request = (re.match(".*api-sirene.*", api_url) and (sirene_key is not None))

        if sirene_request:
            headers["X-INSEE-Api-Key-Integration"] = sirene_key   

        if  sirene_request or (not re.match(".*api-sirene.*", api_url)):

            # avoid reaching the limit of 30 queries per minute from insee api
            _wait_api_query_limit(api_url)

            results = session.get(
                api_url, proxies=proxies, headers=headers, verify=False
            )

            session.close()

            success = True

            code = results.status_code

            if "status_code" not in dir(results):
                success = False
            elif code == 429:
                time.sleep(10)

                request_again = _request_insee(
                    api_url=api_url,
                    sdmx_url=sdmx_url,
                    file_format=file_format,
                    print_msg=print_msg,
                )

                return request_again

            elif code in CODES:
                msg = f"Error {code} - {CODES[code]}\nQuery:\n{api_url}"
                raise requests.exceptions.RequestException(msg)
            elif code != 200:
                success = False

            if success is True:
                return results
            else:
                msg = (
                    "An error occurred !\n"
                    "Query : {api_url}\n"
                    f"{results.text}\n"
                    "Make sure you have subscribed to all APIs !\n"
                    "Click on all APIs' icons one by one, select your "
                    "application, and click on Subscribe"
                )
                raise requests.exceptions.RequestException(msg)

        else:
            # token is None
            commands = "\n\ninit_conn(sirene_key='my_sirene_key')\n"
            msg = (
                "Sirene key is missing, please check your credentials "
                "on portail-api.insee.fr !\n"
                "Please do the following to use your "
                f"credentials: {commands}\n\n"
                "If your token still does not work, please try to clear "
                "the cache :\n "
                "from pynsee.utils import clear_all_cache; clear_all_cache()\n"
            )

            if sdmx_url is not None:
                msg2 = "\nSDMX web service used instead of API"
                if print_msg:
                    logger.critical(msg + msg2)

                results = requests.get(sdmx_url, proxies=proxies, verify=False)

                if results.status_code == 200:
                    return results
                else:
                    raise ValueError(results.text + "\n" + sdmx_url)

            else:
                raise ValueError(msg)
    else:
        # api_url is None
        if sdmx_url is not None:
            results = requests.get(sdmx_url, proxies=proxies, verify=False)

            if results.status_code == 200:
                return results
            else:
                raise ValueError(results.text + "\n" + sdmx_url)

        else:
            raise ValueError("!!! Error : urls are missing")
