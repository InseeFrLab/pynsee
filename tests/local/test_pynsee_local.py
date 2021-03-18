# -*- coding: utf-8 -*-
#proxy
# 
from unittest import TestCase
from pandas import pandas as pd
import geopandas as gpd

from pynsee.local._get_geo_relation import _get_geo_relation
from pynsee.local._get_insee_local import _get_insee_local
from pynsee.local._get_nivgeo import _get_nivgeo
from pynsee.local._get_local_metadata import _get_local_metadata

from pynsee.local.get_geo_list import get_geo_list
from pynsee.local.get_map_link import get_map_link
from pynsee.local.get_map_list import get_map_list
from pynsee.local.get_map import get_map

class TestFunction(TestCase):

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
    
    def test_get_nivgeo(self):
        data = _get_nivgeo()
        self.assertTrue(isinstance(data, pd.DataFrame))
    
    def test_get_local_metadata(self):
        data = _get_local_metadata()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_insee_local(self):            
        variables = 'AGESCOL-SEXE-ETUD'
        dataset = 'GEO2019RP2011'
        codegeo = '91'
        geo = 'DEP'
        data = _get_insee_local(variables, dataset, codegeo, geo)
        self.assertTrue(isinstance(data, pd.DataFrame))