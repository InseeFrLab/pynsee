# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import json
import os

import pytest
import requests

import pynsee.constants
from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils import init_conn

from .patches import (
    clean_os_patch,
    patch_configfile_os_keys,
    patch_retries,
    patch_test_connections,
    patch_test_connections_and_failure_for_sirene,
    save_restore_config,
)


def test_request_insee_1():
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

    assert results.status_code == 200


def test_clear_all_cache():
    clear_all_cache()


@save_restore_config
@clean_os_patch
@patch_retries
def test_init_conn_with_dummy_proxy():
    """Check that a wrong proxy configuration raises a RequestException"""
    with pytest.raises(requests.exceptions.RequestException):
        init_conn(sirene_key="eggs", http_proxy="spam", https_proxy="bacon")


@patch_configfile_os_keys
@patch_test_connections_and_failure_for_sirene
def test_dummy_sirene_token_is_not_stored():
    """
    Check that a wrong SIRENE token is never stored and allows to use other
    APIs still
    """

    with open(pynsee.constants.CONFIG_FILE, "w") as f:
        json.dump({"DUMMY_SIRENE_KEY": "spam"}, f)

    init_conn(sirene_key="eggs")

    with open(pynsee.constants.CONFIG_FILE, "r") as f:
        assert json.load(f)["DUMMY_SIRENE_KEY"] == "spam"


@patch_configfile_os_keys
@clean_os_patch
def test_overriding_insee_config_and_environ():
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
        assert session.sirene_key == "eggs"
        assert session.proxies["https"] == "bacon"


@patch_configfile_os_keys
@clean_os_patch
def test_overriding_insee_config_and_environ2():
    "check that explicit arg has precendence over os.environ"

    os.environ["DUMMY_SIRENE_KEY"] = "eggs"
    os.environ["DUMMY_HTTPS_PROXY_KEY"] = "bacon"

    with PynseeAPISession(sirene_key="spam", https_proxy="sausage") as session:
        # explicit arg has precendence over os.environ
        assert session.sirene_key == "spam"
        assert session.proxies["https"] == "sausage"


@patch_configfile_os_keys
@clean_os_patch
@patch_test_connections
def test_overriding_insee_config_and_environ3():
    "check that init_conn ends with sirene_key/proxies correctly saved"

    init_conn(sirene_key="sausage", https_proxy="spam", http_proxy=None)

    assert os.path.exists(pynsee.constants.CONFIG_FILE)

    with open(pynsee.constants.CONFIG_FILE, "r") as f:
        config = json.load(f)

    assert config["DUMMY_SIRENE_KEY"] == "sausage"
    assert config["DUMMY_HTTPS_PROXY_KEY"] == "spam"
    assert config["DUMMY_HTTP_PROXY_KEY"] is None


@patch_configfile_os_keys
@clean_os_patch
@patch_test_connections
def test_overriding_insee_config_and_environ4():
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
        assert session.sirene_key == "sausage"
        assert session.proxies["http"] is None
        assert session.proxies["https"] == "spam"


if __name__ == "__main__":
    test_request_insee_1()
    test_clear_all_cache()
    test_init_conn_with_dummy_proxy()
    test_dummy_sirene_token_is_not_stored()
    test_overriding_insee_config_and_environ()
    test_overriding_insee_config_and_environ2()
    test_overriding_insee_config_and_environ3()
    test_overriding_insee_config_and_environ4()
