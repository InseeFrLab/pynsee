#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests_cache
import platformdirs


def pytest_sessionstart(session):
    "Add cache to reduce test duration over multiple python version"

    appname = "pynsee-test-http-cache"
    cache_dir = platformdirs.user_cache_dir(appname, ensure_exists=True)
    requests_cache.install_cache(
        cache_name=os.path.join(cache_dir, "requests-cache.sqlite")
    )
