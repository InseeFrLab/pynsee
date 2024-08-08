#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
try:
    import requests_cache
except ModuleNotFoundError:
    pass
import platformdirs
import warnings


def pytest_sessionstart(session):
    "Add cache to reduce test duration over multiple python version"

    appname = "pynsee-test-http-cache"
    cache_dir = platformdirs.user_cache_dir(appname, ensure_exists=True)
    try:
        requests_cache.install_cache(
            cache_name=os.path.join(cache_dir, "requests-cache.sqlite")
        )
    except NameError:
        warnings.warn(
            "requests-cache not preset, http caching will be deactivated "
            "during tests"
            )
