# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import unittest
from unittest import TestCase
import requests

import os
import sys

from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._request_insee import _request_insee
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils.init_conn import init_conn

test_SDMX = True


class TestFunction(TestCase):
    
    version = (sys.version_info[0] == 3) & (sys.version_info[1] == 9)

    if True:
        StartKeys = _get_credentials()

        def test_request_insee_1(self):

            # test both api and sdmx queries fail but token is not none
            sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
            api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

            fail = False

            try:
                _request_insee(sdmx_url=sdmx_url, api_url=api_url)
            except requests.exceptions.RequestException:
                fail = True

            self.assertTrue(fail)

        if test_SDMX:

            def test_request_insee_2(self):
                # if credentials are not well provided but sdmx url works
                clear_all_cache()

                os.environ["sirene_key"] = "key"
                sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
                api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"

                results = _request_insee(api_url=api_url, sdmx_url=sdmx_url)
                test = results.status_code == 200
                self.assertTrue(test)

        def test_clear_all_cache(self):
            test = True
            try:
                clear_all_cache()
            except BaseException:
                test = False
            self.assertTrue(test)


if __name__ == "__main__":
    unittest.main()
