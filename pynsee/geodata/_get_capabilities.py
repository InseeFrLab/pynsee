# -*- coding: utf-8 -*-

import io
from functools import lru_cache
from pynsee.utils.requests_session import PynseeAPISession


@lru_cache(maxsize=None)
def _get_capabilities(key="", version="1.0.0", service="wmts") -> io.BytesIO:

    service_upper = service.upper()

    link = (
        f"https://data.geopf.fr/{service}?SERVICE={service_upper}"
        f"&VERSION={version}&REQUEST=GetCapabilities"
    )

    with PynseeAPISession() as session:

        results = session.get(link, verify=False)
        raw_data_file = io.BytesIO(results.content)

    return raw_data_file
