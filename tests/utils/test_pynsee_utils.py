# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import os
import re
import shutil
import unittest
from unittest import TestCase

import requests

import pynsee.constants
from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils import init_conn


config_file = pynsee.constants.CONFIG_FILE
config_backup = f"{config_file}.back"


def patch_configfile_os_keys(func):
    """
    patch the session with a no-retry policy to speed-up tests intended to get
    http failures
    """

    def wrapper(*args, **kwargs):
        import pynsee.utils._get_credentials

        patched_values = {
            "CONFIG_FILE": "./dummy_config.json",
            "SIRENE_KEY": "DUMMY_SIRENE_KEY",
            "HTTP_PROXY_KEY": "DUMMY_HTTP_PROXY_KEY",
            "HTTPS_PROXY_KEY": "DUMMY_HTTPS_PROXY_KEY",
        }
        init_attrs = {k: getattr(pynsee.constants, k) for k in patched_values}

        for module in [
            pynsee.constants,
            pynsee.utils._get_credentials,
            pynsee.utils.init_connection,
            pynsee.utils.requests_session,
        ]:
            for key, patched in patched_values.items():
                try:
                    getattr(module, key)
                except AttributeError:
                    continue
                setattr(module, key, patched)

        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:

            for module in [
                pynsee.constants,
                pynsee.utils._get_credentials,
                pynsee.utils.init_connection,
                pynsee.utils.requests_session,
            ]:
                for key, init in init_attrs.items():
                    try:
                        getattr(module, key)
                    except AttributeError:
                        continue
                    setattr(module, key, init)

            try:
                print(patched_values["CONFIG_FILE"])
                os.remove(patched_values["CONFIG_FILE"])
            except FileNotFoundError:
                pass

    return wrapper


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


def patch_test_connections_and_failure_for_sirene(func):
    """
    patch the session to simulate a valid connection for each API except SIRENE
    """

    def wrapper(*args, **kwargs):
        init = PynseeAPISession._request_api_insee

        def _request_api_insee(url, *args, **kwargs):
            if re.match(".*api-sirene.*", url):
                dummy_response = object()
                dummy_response.status_code = 400
                raise requests.exceptions.RequestException(
                    response=dummy_response
                )
            else:

                return

        PynseeAPISession._request_api_insee = _request_api_insee
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            PynseeAPISession._request_api_insee = init

    return wrapper


def clean_os_patch(func):
    """
    clean/restore the os variables
    """

    def wrapper(*args, **kwargs):
        keys = (
            "sirene_key",
            "https_proxy",
            "http_proxy",
            "dummy_sirene_key",
            "dummy_https_proxy_key",
            "dummy_http_proxy_key",
        )

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

    @classmethod
    def setup_class(cls):
        """Save config.json"""
        shutil.copy(config_file, config_backup)

    @classmethod
    def teardown_class(cls):
        """Restore config.json"""
        shutil.move(config_backup, config_file)

    def test_request_insee_1(self):
        # if api is not well provided but sdmx url works

        clear_all_cache()

        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
        api_url = "dummy"

        with PynseeAPISession(
            http_proxy="", https_proxy="", sirene_key=""
        ) as session:

            def patch_error_request_api_insee(*args, **kwargs):
                raise requests.exceptions.RequestException

            session._request_api_insee = patch_error_request_api_insee
            results = session.request_insee(api_url=api_url, sdmx_url=sdmx_url)
        self.assertEqual(results.status_code, 200)

    def test_clear_all_cache(self):

        clear_all_cache()
        self.assertTrue(True)

    @clean_os_patch
    @patch_retries
    def test_init_conn_with_dummy_proxy(self):
        "Check that a wrong proxy configuration raises a RequestException"

        with self.assertRaises(requests.exceptions.RequestException):
            init_conn(
                sirene_key="eggs", http_proxy="spam", https_proxy="bacon"
            )

    @patch_configfile_os_keys
    @patch_test_connections_and_failure_for_sirene
    def test_dummy_sirene_token_is_not_stored(self):
        """
        Check that a wrong SIRENE token is never stored and allows to use other
        APIs still
        """

        with open(pynsee.constants.CONFIG_FILE, "w") as f:
            json.dump({"DUMMY_SIRENE_KEY": "spam"}, f)

        init_conn(sirene_key="eggs")

        with open(pynsee.constants.CONFIG_FILE, "r") as f:
            self.assertNotEqual(json.load(f)["DUMMY_SIRENE_KEY"], "eggs")

    @patch_configfile_os_keys
    @clean_os_patch
    def test_overriding_insee_config_and_environ(self):
        "check that os.environ has precendence over previous config"

        with open(pynsee.constants.CONFIG_FILE, "w") as f:
            json.dump(
                {
                    "DUMMY_SIRENE_KEY": "spam",
                    "DUMMY_HTTPS_PROXY_KEY": "sausage",
                },
                f,
            )

        os.environ["DUMMY_SIRENE_KEY"] = "eggs"
        os.environ["DUMMY_HTTPS_PROXY_KEY"] = "bacon"

        with PynseeAPISession() as session:
            self.assertEqual(session.sirene_key, "eggs")
            self.assertEqual(session.proxies["https"], "bacon")

    @patch_configfile_os_keys
    @clean_os_patch
    def test_overriding_insee_config_and_environ2(self):
        "check that explicit arg has precendence over os.environ"

        os.environ["DUMMY_SIRENE_KEY"] = "eggs"
        os.environ["DUMMY_HTTPS_PROXY_KEY"] = "bacon"

        with PynseeAPISession(
            sirene_key="spam", https_proxy="sausage"
        ) as session:
            # explicit arg has precendence over os.environ
            self.assertEqual(session.sirene_key, "spam")
            self.assertEqual(session.proxies["https"], "sausage")

    @patch_configfile_os_keys
    @clean_os_patch
    @patch_test_connections
    def test_overriding_insee_config_and_environ3(self):
        "check that init_conn ends with sirene_key/proxies correctly saved"

        init_conn(sirene_key="sausage", https_proxy="spam", http_proxy=None)

        self.assertTrue(os.path.exists(pynsee.constants.CONFIG_FILE))

        with open(pynsee.constants.CONFIG_FILE, "r") as f:
            config = json.load(f)

        self.assertEqual(config["DUMMY_SIRENE_KEY"], "sausage")
        self.assertEqual(config["DUMMY_HTTPS_PROXY_KEY"], "spam")
        self.assertEqual(config["DUMMY_HTTP_PROXY_KEY"], None)

    @patch_configfile_os_keys
    @clean_os_patch
    @patch_test_connections
    def test_overriding_insee_config_and_environ4(self):
        "check that previous config is restored"

        with open(pynsee.constants.CONFIG_FILE, "w") as f:
            json.dump(
                {
                    "DUMMY_SIRENE_KEY": "sausage",
                    "DUMMY_HTTPS_PROXY_KEY": "spam",
                    "DUMMY_HTTP_PROXY_KEY": None,
                },
                f,
            )

        with PynseeAPISession() as session:
            self.assertEqual(session.sirene_key, "sausage")
            self.assertEqual(session.proxies["http"], None)
            self.assertEqual(session.proxies["https"], "spam")


if __name__ == "__main__":
    unittest.main()
