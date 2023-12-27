# -*- coding: utf-8 -*-

import os
import requests
import tempfile
import urllib3
from functools import lru_cache
from pynsee.utils.requests_params import _get_requests_headers, _get_requests_session, _get_requests_proxies


@lru_cache(maxsize=None)
def _get_capabilities(key='', version="1.0.0", service="wmts", tweak=""):

    service_upper = service.upper()

    #link = "https://wxs.ign.fr/{}/geoportail/{}{}?SERVICE={}&VERSION={}&REQUEST=GetCapabilities".format(
    #    key, tweak, service, service_upper, version
    #)
    link = f"https://data.geopf.fr/{service}?SERVICE={service_upper}&VERSION={version}&REQUEST=GetCapabilities"

    session = _get_requests_session()
    headers = _get_requests_headers()
    proxies = _get_requests_proxies()
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    results = session.get(link, proxies=proxies, headers=headers, verify=False)

    raw_data_file = tempfile.mkdtemp() + "/" + "raw_data_file"

    with open(raw_data_file, "wb") as f:
        f.write(results.content)
        f.close()

    session.close()

    return raw_data_file
