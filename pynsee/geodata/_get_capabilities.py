# -*- coding: utf-8 -*-

import io
import urllib3
from functools import lru_cache
import warnings

from pynsee.utils.requests_params import PynseeAPISession


@lru_cache(maxsize=None)
def _get_capabilities(
    key="", version="1.0.0", service="wmts", tweak=""
) -> io.BytesIO:

    service_upper = service.upper()

    link = f"https://data.geopf.fr/{service}?SERVICE={service_upper}&VERSION={version}&REQUEST=GetCapabilities"

    with PynseeAPISession() as session:

        results = session.get(link, verify=False)
        raw_data_file = io.BytesIO(results.content)

    return raw_data_file
