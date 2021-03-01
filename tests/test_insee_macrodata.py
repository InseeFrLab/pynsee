# -*- coding: utf-8 -*-
#proxy
proxy_file_folder = 'C:/Users/eurhope/Desktop/insee_pylib/insee_pylib'
proxy_file = proxy_file_folder + '/proxy.py'
try:
    f = open(proxy_file)
    exec(f.read())
    print("Proxy file executed")
except IOError:
    print("Proxy file not accessible")

from unittest import TestCase
from pandas import pandas as pd
# from datetime import timedelta 
from datetime import *
import os
#from functools import lru_cache

from insee_macrodata._get_date import _get_date
from insee_macrodata._get_token import _get_token
from insee_macrodata._get_envir_token import _get_envir_token
from insee_macrodata._get_insee import _get_insee
from insee_macrodata._clean_insee_folder import _clean_insee_folder
from insee_macrodata._get_idbank_internal_data_harmonized import _get_idbank_internal_data_harmonized
from insee_macrodata._get_idbank_internal_data import _get_idbank_internal_data
from insee_macrodata._get_dataset_metadata import _get_dataset_metadata
from insee_macrodata._get_dataset_dimension import _get_dataset_dimension
from insee_macrodata._get_dimension_values import _get_dimension_values
from insee_macrodata._get_geo_relation import _get_geo_relation
from insee_macrodata._request_insee import _request_insee
from insee_macrodata._download_idbank_list import _download_idbank_list

from insee_macrodata.get_column_title import get_column_title
from insee_macrodata.search_insee import search_insee

from insee_macrodata.get_dataset_list import get_dataset_list
from insee_macrodata.get_geo_list import get_geo_list
from insee_macrodata.get_idbank_list import get_idbank_list

from insee_macrodata.get_insee_dataset import get_insee_dataset
from insee_macrodata.get_insee_idbank import get_insee_idbank
from insee_macrodata.split_title import split_title

class TestFunction(TestCase):

    def test_get_token(self):        
        token = _get_token()
        self.assertTrue((token is not None))

    def test_get_geo_list_1(self):        
        list_available_geo = ['communes', 'regions', 'departements',
                          'arrondissements', 'arrondissementsMunicipaux']        
        list_geo_data = []
        for geo in list_available_geo:
            list_geo_data.append(get_geo_list(geo))            
        df = pd.concat(list_geo_data)

        self.assertTrue(isinstance(df, pd.DataFrame))
    
    def test_get_geo_list_2(self):   
        self.assertRaises(ValueError, get_geo_list, 'a') 

    def test_get_geo_relation_1(self):    
        df1 = _get_geo_relation('region', "11", 'descendants')
        df2 = _get_geo_relation('departement', "91", 'ascendants')
        test = isinstance(df1, pd.DataFrame) & isinstance(df2, pd.DataFrame)
        self.assertTrue(test)        
    
    def test_get_dataset_list(self):        
        data = get_dataset_list()
        self.assertTrue(isinstance(data, pd.DataFrame))
    
    def test_get_column_title_1(self):     
        _clean_insee_folder()
        data1 = get_column_title()
        test1 = isinstance(data1, pd.DataFrame)

        data2 = get_column_title(['CLIMAT-AFFAIRES', 'IPC-2015'])
        test2 = isinstance(data2, pd.DataFrame)
        self.assertTrue(test1 & test2)

    def test_get_column_title_2(self):   
        self.assertRaises(ValueError, get_column_title, dataset = ['a']) 
    
    def test_get_idbank_list_1(self):        
        data = get_idbank_list('CLIMAT-AFFAIRES')
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_idbank_list_2(self):   
        self.assertRaises(ValueError, get_idbank_list, 'a')    
        

    def test_get_insee_idbank_1(self):
        idbank_list = get_idbank_list('IPC-2015').iloc[:900]
        data = get_insee_idbank(idbank_list.idbank)
        self.assertTrue(isinstance(data, pd.DataFrame))
        
    def test_get_insee_idbank_2(self):
        data = get_insee_idbank("001769682", "001769683")
        self.assertTrue(isinstance(data, pd.DataFrame))
    
    def test_get_insee_idbank_3(self):
        data = get_insee_idbank(["001769683", "001769682"], lastNObservations=1)
        self.assertTrue(isinstance(data, pd.DataFrame))
    
    def test_get_date(self):
        data = get_insee_idbank("001694056", "001691912",
         "001580062", "001688370", "010565692", "001580394")
        test1 = isinstance(data, pd.DataFrame)
        test2 = (_get_date(freq = 'TEST', time_period = 3) == 3)
        self.assertTrue(test1 & test2)
    
    def test_get_insee(self):
        data = _get_insee(
            api_query = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001769682",
            sdmx_query = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001769682")        
        test1 = isinstance(data, pd.DataFrame)
      
        data = _get_insee(
            api_query = "https://api.insee.fr/series/BDM/V1/data/BALANCE-PAIEMENTS",
            sdmx_query = "https://bdm.insee.fr/series/sdmx/data/BALANCE-PAIEMENTS")
        test2 = isinstance(data, pd.DataFrame)

        self.assertTrue(test1 & test2)
        
    def test_get_insee_dataset_1(self):
        data = get_insee_dataset('BALANCE-PAIEMENTS')
        self.assertTrue(isinstance(data, pd.DataFrame))
    
    def test_get_insee_dataset_2(self):
        data = get_insee_dataset("CNA-2014-CPEB",
                              filter = "A.CNA_CPEB.A38-CB.VAL.D39.VALEUR_ABSOLUE.FE.EUROS_COURANTS.BRUT",
                              lastNObservations = 1)
        self.assertTrue(isinstance(data, pd.DataFrame))
        
    def test_get_insee_dataset_3(self):
        data1 = get_insee_dataset("IPC-2015", filter = "M......ENSEMBLE...CVS.2015")
        data2 = get_insee_dataset("IPC-2015", filter = "M......ENSEMBLE...CVS.2015",
                   includeHistory = True,
                   updatedAfter = "2017-07-11T08:45:00")        
        self.assertTrue(len(data1.index) < len(data2.index))
    
    def test_get_insee_dataset_4(self):   
        self.assertRaises(ValueError, get_insee_dataset, 'a')   
        
    def test_split_title(self):
        data = get_insee_idbank("001769682", "001769683")   
        df1 = split_title(data)
        # main test
        test1 = isinstance(df1, pd.DataFrame)
        # test is object is dataframe
        test2 = (split_title(1) == 1)
        # test if title column exists
        df3 = split_title(data, title_col_name=['ABC'])
        test3 = (len(df3.columns) < len(df1.columns))
        # test if n_split is not doable
        df4 = split_title(data, n_split=100)
        test4 = isinstance(df4, pd.DataFrame)
        df5 = split_title(data, n_split=-10)
        test5 = isinstance(df5, pd.DataFrame)
        self.assertTrue(test1 & test2 & test3 & test4 & test5)
       
    def test_search_insee(self):
        search_all = search_insee()
        search_paris = search_insee("PARIS")
        test1 = isinstance(search_all, pd.DataFrame)
        test2 = isinstance(search_paris, pd.DataFrame)
        self.assertTrue(test1 & test2)

    def test_get_idbank_internal_data(self):
        df = _get_idbank_internal_data()        
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_idbank_internal_data_harmonized(self):
        df = _get_idbank_internal_data_harmonized()        
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_dataset_metadata(self):  
        from datetime import datetime
        from datetime import timedelta
        
        df = _get_dataset_metadata('CLIMAT-AFFAIRES')
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _get_dataset_metadata('CLIMAT-AFFAIRES')

        test1 = isinstance(df, pd.DataFrame)

        df = _get_dataset_metadata('CLIMAT-AFFAIRES', update=True)
        test2 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1 & test2)

    def test_get_dataset_dimension(self):  
        from datetime import datetime
        from datetime import timedelta

        df = _get_dataset_dimension('CLIMAT-AFFAIRES')
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _get_dataset_dimension('CLIMAT-AFFAIRES')

        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)
    
    def test_get_dimension_values(self):  
        from datetime import datetime
        from datetime import timedelta

        df = _get_dimension_values('CL_PERIODICITE')
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _get_dimension_values('CL_PERIODICITE')

        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)
    
    def test_request_insee(self):
        # if credentials are not well provided but sdmx url works
        os.environ['insee_key'] = "key"
        os.environ['insee_secret'] = "secret"
        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
        api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"

        results = _request_insee(api_url=api_url, sdmx_url=sdmx_url)
        test = (results.status_code == 200)
        self.assertTrue(test)

    def test_get_envir_token(self):
        # if credentials are not well provided but sdmx url works       
        os.environ['insee_token'] = "a"    
        token = _get_envir_token()  
        test = (token is None)  
        self.assertTrue(test)

    def test_download_idbank_list_0(self):   
        df = _download_idbank_list()
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)
    
    def test_download_idbank_list_1(self):  
        from datetime import datetime
        from datetime import timedelta
     
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _download_idbank_list()

        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)

    def test_download_idbank_list_2(self):  
        _clean_insee_folder() 
        os.environ['insee_idbank_file_csv'] = "test_file"
        self.assertRaises(ValueError, _download_idbank_list)

    def test_download_idbank_list_3(self):
        _clean_insee_folder()
        os.environ['insee_idbank_file_to_dwn'] = "https://www.insee.fr/en/statistiques/fichier/test"
        self.assertRaises(ValueError, _download_idbank_list)


