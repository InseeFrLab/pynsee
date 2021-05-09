# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from unittest import TestCase
from pandas import pandas as pd

import os

from pynsee.utils._get_token import _get_token
from pynsee.utils._get_envir_token import _get_envir_token
from pynsee.utils._clean_insee_folder import _clean_insee_folder
from pynsee.utils._request_insee import _request_insee
from pynsee.utils.clear_all_cache import clear_all_cache

class TestFunction(TestCase):

    def test_get_token(self):        
        token = _get_token()
        self.assertTrue((token is not None))

    def test_request_insee_0(self):
        # test both api and sdmx queries fail but token is not none        
        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/CLIMAT-AFFAIRES"
        api_url = "https://api.insee.fr/series/BDM/V1/data/CLIMAT-AFFAIRE_test"
       
        def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
            _request_insee(sdmx_url=sdmx_url, api_url=api_url)

        self.assertRaises(ValueError, request_insee_test)
    
    def test_request_insee_1(self):
        # test both api and sdmx queries fail but token is not none        
        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
        api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"
       
        def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
            _request_insee(sdmx_url=sdmx_url, api_url=api_url)

        self.assertRaises(ValueError, request_insee_test)

    def test_request_insee_2(self):
        # if credentials are not well provided but sdmx url works
        _get_token.cache_clear()
        _get_envir_token.cache_clear() 

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
        # if credentials are not well provided but sdmx url works   
        _get_envir_token.cache_clear()    
        os.environ['insee_token'] = "a"    
        token = _get_envir_token()  
        test = (token is None)  
        self.assertTrue(test)

    def test_clear_all_cache(self):
        test = True
        try:
            clear_all_cache()
        except:
            test = False
        self.assertTrue(test)
            
        
        
        