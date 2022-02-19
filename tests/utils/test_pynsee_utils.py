# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import unittest
from unittest import TestCase

import os
import sys

from pynsee.utils._get_token import _get_token
from pynsee.utils._get_envir_token import _get_envir_token
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._request_insee import _request_insee
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils.init_conn import init_conn
from pynsee.utils._get_credentials import _get_credentials

test_SDMX = True

os.environ['pynsee_query_print'] = 'True'


class TestFunction(TestCase):

    version_3_7 = (sys.version_info[0] == 3) & (sys.version_info[1] == 7)

    if not version_3_7:

        StartKeys = _get_credentials()

        def test_get_token(self, StartKeys=StartKeys):

            insee_key = StartKeys['insee_key']
            insee_secret = StartKeys['insee_secret']

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

            self.assertRaises(ValueError, request_insee_test)

        if test_SDMX:
            def test_request_insee_2(self):
                # if credentials are not well provided but sdmx url works
                clear_all_cache()

                os.environ['insee_token'] = "test"
                os.environ['insee_key'] = "key"
                os.environ['insee_secret'] = "secret"
                sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
                api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"

                results = _request_insee(api_url=api_url, sdmx_url=sdmx_url)
                test = (results.status_code == 200)
                self.assertTrue(test)

        def test_request_insee_3(self):
            # token is none and sdmx query fails
            
            init_conn(insee_key = "test", insee_secret="test")

            _get_token.cache_clear()
            _get_envir_token.cache_clear()

            os.environ['insee_token'] = "test"
            os.environ['insee_key'] = "key"
            os.environ['insee_secret'] = "secret"
            sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
            api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(ValueError, request_insee_test)

        def test_request_insee_4(self):
            # token is none and sdmx query is None
            # _get_token.cache_clear()
            # _get_envir_token.cache_clear()
            clear_all_cache()

            os.environ['insee_token'] = "test"
            os.environ['insee_key'] = "key"
            os.environ['insee_secret'] = "secret"
            api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=None, api_url=api_url):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(ValueError, request_insee_test)

        def test_request_insee_5(self):
            # api query is none and sdmx query fails
            sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"

            def request_insee_test(sdmx_url=sdmx_url, api_url=None):
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)

            self.assertRaises(ValueError, request_insee_test)

        def test_get_envir_token(self):

            _get_envir_token.cache_clear()
            os.environ['insee_token'] = "a"
            token = _get_envir_token()
            test = (token is None)
            self.assertTrue(test)

        def test_clear_all_cache(self):
            test = True
            try:
                clear_all_cache()
            except BaseException:
                test = False
            self.assertTrue(test)


if __name__ == '__main__':
    unittest.main()