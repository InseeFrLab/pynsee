import logging
import os
import re
import time
import warnings

import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry
from requests_ratelimiter import LimiterAdapter
from pyrate_limiter import SQLiteBucket

import pynsee
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._create_insee_folder import _create_insee_folder

logger = logging.getLogger(__name__)


class PynseeAPISession(requests.Session):
    """
    Session class used to allow specific timeouts and
    """

    INSEE_API_CODES = {
        # 200:"Opération réussie",
        # 301:"Moved Permanently" -> r.headers['location']
        400: "Bad Request",
        401: "Unauthorized : token missing",
        403: "Forbidden : missing subscription to API",  #
        # 404: "Not Found : no results available",
        406: "Not acceptable : incorrect 'Accept' header",
        413: "Too many results, query must be splitted",
        414: "Request-URI Too Long",
        # Unused (managed through a specific if/else), kept for memory purpose
        # 429: "Too Many Requests : allocated quota overloaded",
        500: "Internal Server Error ",
        503: "Service Unavailable",
    }

    def __init__(self):

        super().__init__()

        # default retries adapter
        retry_adapt = Retry(total=3, backoff_factor=1, status_forcelist=[502])
        adapter = HTTPAdapter(max_retries=retry_adapt)
        self.mount("https://", adapter)
        self.mount("https://", adapter)

        insee_folder = _create_insee_folder()
        rate_folder = os.path.join(insee_folder, "rate_limiter")

        # the sent custom adapters for each API, to allow a separate rate
        # tracking for each
        def kw_adapter(api: str):
            return {
                "max_retries": retry_adapt,
                "bucket_class": SQLiteBucket,
                "bucket_kwargs": {
                    "path": os.path.join(rate_folder, f"{api}.db"),
                    "isolation_level": "EXCLUSIVE",
                    "check_same_thread": False,
                },
            }

        # 30 queries/min for SIRENE
        sirene_adapter = LimiterAdapter(per_minute=30, **kw_adapter("sirene"))
        self.mount("https://api.insee.fr/api-sirene", sirene_adapter)

        # 30 queries/min for BDM: from documentation, though there is no
        # need of a token?!
        bdm_adapter = LimiterAdapter(per_minute=30, **kw_adapter("bdm"))
        self.mount("https://api.insee.fr/series/BDM", bdm_adapter)

        # 30 queries/min for (old) localdata API: from documentation, though
        # there is need of a token!?
        metadata_adapter = LimiterAdapter(
            per_minute=30, **kw_adapter("localdata")
        )
        self.mount("https://api.insee.fr/donnees-locales", metadata_adapter)

        # 30 queries/min for (new) melodi API: from documentation, though
        # there is need of a token!?
        melodi_adapter = LimiterAdapter(per_minute=30, **kw_adapter("melodi"))
        self.mount("https://api.insee.fr/melodi", melodi_adapter)

        # 10_000 queries/min for metadata API: from subscription page, though
        # there is need of a token!?
        metadata_adapter = LimiterAdapter(
            per_minute=10_000, **kw_adapter("metadata")
        )
        self.mount("https://api.insee.fr/metadonnees/", metadata_adapter)

        proxies = {
            "http": os.environ.get("http_proxy", ""),
            "https": os.environ.get("https_proxy", ""),
        }
        self.headers.update(proxies)

        username = os.environ.get("USERNAME", "username")
        version = pynsee.__version__
        useragent = {"User-Agent": f"python_pynsee_{username}/{version}"}

        # Note : geoplatform seems to impose the "/version" to the user-agent
        self.headers.update(useragent)

        self.sirene_key = _get_credentials().get("sirene_key", None)
        self.headers["X-INSEE-Api-Key-Integration"] = self.sirene_key

    def request(
        self, method, url, timeout=(5, 10), raise_if_not_ok=True, **kwargs
    ):

        logger.info(url)
        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore", urllib3.exceptions.InsecureRequestWarning
            )
            response = super().request(method, url, timeout=(5, 10), **kwargs)
            if raise_if_not_ok and not response.ok:
                raise requests.exceptions.RequestException(
                    f"response was {response.status_code} for {url}",
                    response=response,
                )
        return response

    def request_insee(
        self,
        api_url=None,
        sdmx_url=None,
        file_format="application/xml",
        print_msg=True,
        raise_if_not_ok=False,
    ):
        "Performs a query to insee, either through API or sdmx_url"
        result = None

        try:
            if api_url and self._query_is_valid_sirene_call(api_url):
                if not self.sirene_key:
                    commands = "\n\ninit_conn(sirene_key='my_sirene_key')\n"
                    msg = (
                        "Sirene key is missing, please check your credentials "
                        "on portail-api.insee.fr !\n"
                        "Please do the following to use your "
                        f"credentials: {commands}\n\n"
                        "If your token still does not work, please try to "
                        "clear the cache :\n "
                        "from pynsee.utils import clear_all_cache;"
                        " clear_all_cache()\n"
                    )
                    raise ValueError(msg)

                self._set_sirene_key()

            if api_url:
                result = self._request_api_insee(
                    api_url,
                    file_format=file_format,
                    raise_if_not_ok=raise_if_not_ok,
                    print_msg=print_msg,
                )

        except ValueError as e:

            if self._query_is_valid_sirene_call(api_url):
                # Log the error as a SIRENE API call can not function without
                # key
                logger.critical(e)

        except requests.exceptions.RequestException:
            if sdmx_url:
                if print_msg:
                    logger.critical("SDMX web service used instead of API")
                result = self._request_sdmx_insee(
                    sdmx_url, raise_if_not_ok=raise_if_not_ok
                )

        return result

    def _query_is_valid_sirene_call(self, url):
        "check if an URL is a valid API call to SIRENE"
        return re.match(".*api-sirene.*", url)

    def _set_sirene_key(self):

        sirene_key = _get_credentials().get("sirene_key", None)
        if not sirene_key:
            raise ValueError
        self.headers["X-INSEE-Api-Key-Integration"] = sirene_key

    def _request_sdmx_insee(self, url, raise_if_not_ok=True):
        results = self.get(url, verify=False)
        if raise_if_not_ok and not results.ok:
            raise requests.exceptions.RequestException(
                results.text + "\n" + url, response=results
            )
        return results

    def _request_api_insee(
        self,
        url,
        file_format="application/xml",
        raise_if_not_ok=False,
        print_msg=True,
    ):

        headers = {"Accept": file_format}

        try:
            results = self.get(
                url,
                headers=headers,
                verify=False,
                raise_if_not_ok=raise_if_not_ok,
            )
        except Exception:
            results = None
            success = False
        else:

            code = results.status_code

            if "status_code" not in dir(results):
                success = False
            elif code == 429:

                if (
                    os.environ.get(
                        "PYNSEE_DISPLAY_ALL_WARNINGS", "false"
                    ).lower()
                    == "true"
                ):
                    msg = (
                        "API query number limit reached - "
                        "function might be slowed down"
                    )
                    logger.warning(msg)

                time.sleep(10)

                request_again = self._request_api_insee(
                    url=url, file_format=file_format
                )

                return request_again

            elif code in self.INSEE_API_CODES and raise_if_not_ok:
                msg = (
                    f"Error {code} - {self.INSEE_API_CODES[code]}\n"
                    f"Query:\n{url}"
                )
                raise requests.exceptions.RequestException(
                    msg, response=results
                )
            elif code not in (200, 404) and raise_if_not_ok:
                # Note : 404 means no results from API, this should not trigger
                # any exception
                success = False
            else:
                success = True

        if success is True:
            return results

        else:

            try:
                results = results.text
            except Exception:
                results = ""

            if print_msg:
                msg = (
                    "An error occurred !\n"
                    f"Query : {url}\n{results}\n"
                    "Make sure you have subscribed to all APIs !\n"
                    "Click on all APIs' icons one by one, select your "
                    "application, and click on Subscribe"
                )

                logger.warning(msg)
            raise requests.exceptions.RequestException(
                "Une erreur est survenue", response=results
            )


# if __name__ == "__main__":
#     s = PynseeAPISession()
#     url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"
#     r = s.get(url)
#     print(r)
