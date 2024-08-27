#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
import os

try:
    import requests_cache
except ModuleNotFoundError:
    pass
import platformdirs
import warnings


def pytest_addoption(parser):
    parser.addoption(
        "--clean-cache",
        action="store_true",
        help="remove previous tests' cache",
    )

    parser.addoption(
        "--no-cache",
        action="store_true",
        help="disable cache during tests",
    )


def pytest_sessionstart(session):
    "Add cache to reduce test duration over multiple python version"

    appname = "pynsee-test-http-cache"
    cache_dir = platformdirs.user_cache_dir(appname, ensure_exists=True)

    cache_name = os.path.join(cache_dir, "requests-cache.sqlite")
    clean_cache = session.config.getoption("--clean-cache")
    if clean_cache:
        os.unlink(cache_name)

    no_cache = session.config.getoption("--no-cache")
    if no_cache:
        return

    try:
        requests_cache.install_cache(
            cache_name=cache_name, expire_after=timedelta(days=30)
        )
    except NameError:
        warnings.warn(
            "requests-cache not preset, http caching will be deactivated "
            "during tests"
        )
