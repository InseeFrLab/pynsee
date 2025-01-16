import logging
import os
import urllib3
import warnings

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
import tenacity._utils

logger = logging.getLogger(__name__)


def _get_requests_headers():

    username = os.environ.get("USERNAME", "username")

    headers = {"User-Agent": f"python_pynsee_{username}"}
    return headers


def _get_requests_proxies():

    proxies = {
        "http": os.environ.get("http_proxy", ""),
        "https": os.environ.get("https_proxy", ""),
    }

    return proxies


class PynseeAPISession(requests.Session):
    """
    Session class used to allow specific timeouts and
    """

    def __init__(self):

        super().__init__()

        retry = Retry(total=8, connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        self.mount("https://", adapter)
        self.mount("https://", adapter)
        self.headers.update(_get_requests_proxies())
        self.headers.update(_get_requests_headers())

    @staticmethod
    def after_log(
        logger: "logging.Logger",
        log_level: int,
        sec_format: str = "%0.3f",
    ):
        "Log every retry."

        def log_it(retry_state):
            try:
                retry_state.outcome.result()
            except Exception:
                logger.log(
                    log_level,
                    f"{tenacity._utils.to_ordinal(retry_state.attempt_number)}"
                    f" request call to with args={retry_state.args[1:]} "
                    f"after {sec_format % retry_state.seconds_since_start}s.",
                )

        return log_it

    @staticmethod
    def traceback_after_retries(retry_state):
        logger.error(
            "An error happened to request call with"
            f"args={retry_state.args[1:]}"
        )
        return retry_state.outcome.result()

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        after=after_log(logger, logging.WARNING),
        retry_error_callback=traceback_after_retries,
    )
    def request(self, method, url, timeout=30, **kwargs):

        logger.info(url)
        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore", urllib3.exceptions.InsecureRequestWarning
            )
            response = super().request(method, url, timeout=timeout, **kwargs)
        return response
