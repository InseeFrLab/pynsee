# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
import requests
import sys
import unittest

from unittest import TestCase

import pynsee
from pynsee.utils._get_token import _get_token
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._request_insee import _request_insee
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils.init_conn import init_conn
from pynsee.utils._get_credentials import _get_credentials

test_SDMX = True


def save_restore_cred(func):
    def wrapper(*args, **kwargs):
        saved_token = pynsee.get_config("insee_token")
        saved_key = pynsee.get_config("insee_key")
        saved_secret = pynsee.get_config("insee_secret")

        res = func(*args, **kwargs)

        pynsee.set_config("insee_token", saved_token)
        pynsee.set_config("insee_key", saved_key)
        pynsee.set_config("insee_secret", saved_secret)

        return res
    return wrapper


class TestFunction(TestCase):
    version_3_7 = (sys.version_info[0] == 3) & (sys.version_info[1] == 7)

    if not version_3_7:
        def test_get_token(self):
            insee_key = pynsee.get_config("insee_key")
            insee_secret = pynsee.get_config("insee_secret")

            init_conn(insee_key=insee_key, insee_secret=insee_secret)
            keys = _get_credentials()

            token = _get_token(insee_key, insee_secret)
            self.assertTrue((token is not None))

        def test_request_insee_1(self):
            # test both api and sdmx queries fail but token is not none
            sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
            api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(
                requests.exceptions.RequestException, request_insee_test
            )

        if test_SDMX:
            @save_restore_cred
            def test_request_insee_2(self):
                # if credentials are not well provided but sdmx url works
                clear_all_cache()

                pynsee.set_config("insee_token", "test")
                pynsee.set_config("insee_key", "key")
                pynsee.set_config("insee_secret", "secret")

                sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
                api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"

                results = _request_insee(api_url=api_url, sdmx_url=sdmx_url)
                test = results.status_code == 200
                self.assertTrue(test)

        @save_restore_cred
        def test_request_insee_3(self):
            # token is none and sdmx query fails
            def init_conn_foo():
                init_conn(insee_key="test", insee_secret="test")

            self.assertRaises(ValueError, init_conn_foo)

            pynsee.set_config("insee_token", "test")
            pynsee.set_config("insee_key", "key")
            pynsee.set_config("insee_secret", "secret")

            sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
            api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(requests.exceptions.RequestException,
                              request_insee_test)

        def test_request_insee_4(self):
            # token is none and sdmx query is None
            clear_all_cache()

            pynsee.set_config("insee_token", "test")
            pynsee.set_config("insee_key", "key")
            pynsee.set_config("insee_secret", "secret")

            api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=None, api_url=api_url):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(requests.exceptions.RequestException,
                              request_insee_test)

        def test_request_insee_5(self):
            # api query is none and sdmx query fails
            sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=sdmx_url, api_url=None):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(ValueError, request_insee_test)

        def test_get_envir_token(self):
            old_token = pynsee.get_config("insee_token")
            os.environ["insee_token"] = "a"
            _get_token()
            test = pynsee.get_config("insee_token") == "a"
            self.assertTrue(test)

            # restore token
            if old_token:
                pynsee.set_config("insee_token", old_token)

        def test_clear_all_cache(self):
            test = True
            try:
                clear_all_cache()
            except BaseException:
                test = False
            self.assertTrue(test)


if __name__ == "__main__":
    unittest.main()
