# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import os
import unittest
from unittest import TestCase

from platformdirs import user_config_dir
import requests

from pynsee.utils._get_credentials import _get_credentials_from_configfile
from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils.init_conn import init_conn


def patch_retries(func):
    """
    patch the session with a no-retry policy to speed-up tests intended to get
    http failures
    """

    def wrapper(*args, **kwargs):
        init = PynseeAPISession._mount_adapters
        PynseeAPISession._mount_adapters = lambda x: None
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            PynseeAPISession._mount_adapters = init

    return wrapper


def patch_test_connections(func):
    """
    patch the session to simulate a valid connection for each API
    """

    def wrapper(*args, **kwargs):
        init = PynseeAPISession._test_connections
        PynseeAPISession._test_connections = lambda x: {}
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            PynseeAPISession._test_connections = init

    return wrapper


def clean_os_patch(func):
    """
    clean/restore the os variables
    """

    def wrapper(*args, **kwargs):
        keys = "sirene_key", "https_proxy", "http_proxy"
        keys = list(keys) + [x.upper() for x in keys]
        init = {k: os.environ[k] for k in keys if k in os.environ}
        for k in init:
            del os.environ[k]
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            for k in keys:
                try:
                    del os.environ[k]
                except KeyError:
                    pass
            os.environ.update(init)

    return wrapper


class TestFunction(TestCase):

    StartKeys = _get_credentials_from_configfile()

    def test_request_insee_1(self):
        # if api is not well provided but sdmx url works

        clear_all_cache()

        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
        api_url = (
            "https://api.insee.dummy/series/BDM/V1/data/SERIES_BDM/001688370"
        )

        with PynseeAPISession(
            http_proxy="", https_proxy="", sirene_key=""
        ) as session:
            results = session.request_insee(api_url=api_url, sdmx_url=sdmx_url)
        test = results.status_code == 200
        self.assertTrue(test)

    def test_clear_all_cache(self):

        clear_all_cache()
        self.assertTrue(True)

    @clean_os_patch
    @patch_retries
    def test_init_conn_with_dummy_proxy(self):
        "Check that a wrong proxy configuration raises a RequestException"

        with self.assertRaises(requests.exceptions.RequestException):
            os.environ["http_proxy"] = "spam"
            os.environ["https_proxy"] = "bacon"
            init_conn(sirene_key="eggs")

    @patch_retries
    def test_dummy_sirene_token_is_not_stored(self):
        "Check that a wrong SIRENE token is never stored"

        config_file = os.path.join(
            user_config_dir("pynsee", ensure_exists=True), "config.json"
        )
        with open(config_file, "w") as f:
            json.dump({"sirene_key": "spam"}, f)

        init_conn(sirene_key="eggs")

        config_file = os.path.join(
            user_config_dir("pynsee", ensure_exists=True), "config.json"
        )
        with open(config_file, "r") as f:
            self.assertFalse(json.load(f)["sirene_key"] == "eggs")

    @clean_os_patch
    @patch_test_connections
    def test_overriding_insee_config_and_environ(self):
        "check that the order of precedance for config keys is respected"

        config_file = os.path.join(
            user_config_dir("pynsee", ensure_exists=True), "config.json"
        )
        with open(config_file, "w") as f:
            json.dump({"sirene_key": "spam", "https_proxy": "sausage"}, f)

        os.environ["sirene_key"] = "eggs"
        os.environ["https_proxy"] = "bacon"

        with PynseeAPISession() as session:
            # os.environ has precendence over previous config
            self.assertTrue(session.sirene_key == "eggs")
            self.assertTrue(session.proxies["https"] == "bacon")

        with PynseeAPISession(
            sirene_key="spam", https_proxy="sausage"
        ) as session:
            # explicit arg has precendence over os.environ
            self.assertTrue(session.sirene_key == "spam")
            self.assertTrue(session.proxies["https"] == "sausage")

        for key in "sirene_key", "https_proxy", "http_proxy":
            try:
                del os.environ[key]
            except KeyError:
                pass

        init_conn(sirene_key="sausage", https_proxy="spam", http_proxy=None)
        with open(config_file, "r") as f:
            # confirm init_conn ends with sirene_key/proxies correctly saved
            config = json.load(f)
        self.assertTrue(config["sirene_key"] == "sausage")
        self.assertTrue(config["https_proxy"] == "spam")
        self.assertTrue(config["http_proxy"] is None)

        with PynseeAPISession() as session:
            # confirm that previous config is restored
            self.assertTrue(session.sirene_key == "sausage")
            self.assertTrue(session.proxies["http"] is None)
            self.assertTrue(session.proxies["https"] == "spam")


if __name__ == "__main__":
    unittest.main()
