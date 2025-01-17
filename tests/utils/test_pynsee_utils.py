# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import unittest
from unittest import TestCase

from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils.requests_session import PynseeAPISession
from pynsee.utils.clear_all_cache import clear_all_cache


class TestFunction(TestCase):

    StartKeys = _get_credentials()

    def test_request_insee_1(self):
        # if api is not well provided but sdmx url works
        clear_all_cache()

        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
        api_url = (
            "https://api.insee.dummy/series/BDM/V1/data/SERIES_BDM/001688370"
        )

        with PynseeAPISession() as session:
            results = session.request_insee(api_url=api_url, sdmx_url=sdmx_url)
        test = results.status_code == 200
        self.assertTrue(test)

    def test_clear_all_cache(self):

        clear_all_cache()
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
