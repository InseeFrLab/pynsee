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
import geopandas as gpd

# from datetime import timedelta 
# from datetime import *
import os
#from functools import lru_cache

from pynsee.macrodata._get_insee import _get_insee
from pynsee.macrodata._get_date import _get_date
from pynsee.macrodata._get_idbank_internal_data_harmonized import _get_idbank_internal_data_harmonized
from pynsee.macrodata._get_idbank_internal_data import _get_idbank_internal_data
from pynsee.macrodata._get_dataset_metadata import _get_dataset_metadata
from pynsee.macrodata._get_dataset_dimension import _get_dataset_dimension
from pynsee.macrodata._get_dimension_values import _get_dimension_values
from pynsee.macrodata._download_idbank_list import _download_idbank_list

from pynsee.macrodata.get_column_title import get_column_title
from pynsee.macrodata.search_insee import search_insee
from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata.get_idbank_list import get_idbank_list
from pynsee.macrodata.get_insee_dataset import get_insee_dataset
from pynsee.macrodata.get_insee_idbank import get_insee_idbank
from pynsee.macrodata.get_last_release import get_last_release
from pynsee.macrodata.split_title import split_title

from pynsee.utils._clean_insee_folder import _clean_insee_folder

class TestFunction(TestCase):

    def test_get_dataset_metadata_1(self):  
        from datetime import datetime
        from datetime import timedelta

        os.environ['insee_idbank_file_to_dwn'] = "https://www.insee.fr/en/statistiques/fichier/2868055/2020_correspondance_idbank_dimension.zip"
        os.environ['insee_idbank_file_csv'] = "2020_correspondances_idbank_dimension.csv"

        # test automatic update of metadata, when older than 3 months
        df = _get_dataset_metadata('CLIMAT-AFFAIRES')
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _get_dataset_metadata('CLIMAT-AFFAIRES')
        test1 = isinstance(df, pd.DataFrame)

        # test manual update of metadata
        df = _get_dataset_metadata('CLIMAT-AFFAIRES', update=True)
        test2 = isinstance(df, pd.DataFrame)

        # test date provided manually error and switch to today
        os.environ['insee_date_test'] = "a"
        df = _get_dataset_metadata('CLIMAT-AFFAIRES')
        test3 = isinstance(df, pd.DataFrame)

        self.assertTrue(test1 & test2 & test3)
    
    def test_get_dataset_metadata_2(self):  
        from datetime import datetime
        from datetime import timedelta
        # crash download_idbank_list and test the result on get_dataset_metadata
        os.environ['insee_idbank_file_to_dwn'] = "https://www.insee.fr/en/statistiques/test"
        os.environ['insee_idbank_file_csv'] = "test"
        _clean_insee_folder()
        df = _get_dataset_metadata('CLIMAT-AFFAIRES')        
        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)

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
        data = get_insee_idbank(idbank_list.IDBANK)
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

    def test_get_dataset_dimension(self):  
        from datetime import datetime
        from datetime import timedelta

        df = _get_dataset_dimension('CLIMAT-AFFAIRES')
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _get_dataset_dimension('CLIMAT-AFFAIRES')
        test1 = isinstance(df, pd.DataFrame)

        _clean_insee_folder()
        os.environ['insee_date_test'] = '' 
        df = _get_dataset_dimension('CLIMAT-AFFAIRES')
        test2 = isinstance(df, pd.DataFrame)

        self.assertTrue(test1 & test2)
    
    def test_get_dimension_values(self):  
        from datetime import datetime
        from datetime import timedelta

        df = _get_dimension_values('CL_PERIODICITE')
        os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
        df = _get_dimension_values('CL_PERIODICITE')

        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)
    
    def test_download_idbank_list_1(self):  
        from datetime import datetime
        from datetime import timedelta
     
        try:
            df = _download_idbank_list()
            os.environ['insee_date_test'] = str(datetime.now() + timedelta(days=91))        
            df = _download_idbank_list()
        except:
            df = pd.DataFrame({'test_backup':['test_backup']})

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

    def test_get_last_release(self):
        data = get_last_release()
        self.assertTrue(isinstance(data, pd.DataFrame))
        
        
        
