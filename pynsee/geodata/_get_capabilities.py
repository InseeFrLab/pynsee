# -*- coding: utf-8 -*-

import io
import urllib3
from functools import lru_cache
from pynsee.utils.requests_params import (
    _get_requests_headers,
    _get_requests_session,
    _get_requests_proxies,
)


@lru_cache(maxsize=None)
def _get_capabilities(key="", version="1.0.0", service="wmts") -> io.BytesIO:

    service_upper = service.upper()

    link = f"https://data.geopf.fr/{service}?SERVICE={service_upper}&VERSION={version}&REQUEST=GetCapabilities"

    session = _get_requests_session()
    headers = _get_requests_headers()
    proxies = _get_requests_proxies()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    results = session.get(link, proxies=proxies, headers=headers, verify=False)

    raw_data_file = io.BytesIO(results.content)

    return raw_data_file
