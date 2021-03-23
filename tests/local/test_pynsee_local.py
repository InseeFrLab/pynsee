# -*- coding: utf-8 -*-
#proxy
# 
from unittest import TestCase
from pandas import pandas as pd
import geopandas as gpd
import sys

from pynsee.local._get_geo_relation import _get_geo_relation
from pynsee.local.get_insee_local import get_insee_local
from pynsee.local.get_nivgeo_list import get_nivgeo_list
from pynsee.local.get_local_metadata import get_local_metadata

from pynsee.local.get_geo_list import get_geo_list
from pynsee.local.get_map_link import get_map_link
from pynsee.local.get_map import get_map

class TestFunction(TestCase):

    version_3_7 = (sys.version_info[0]==3) & (sys.version_info[1]==7)
    
    if version_3_7:
    
        def test_get_geo_list_1(self):        
            list_available_geo = ['communes', 'regions', 'departements',
                                'communesDeleguees', 'communesAssociees',
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
        
        def test_get_nivgeo_list(self):
            data = get_nivgeo_list()
            self.assertTrue(isinstance(data, pd.DataFrame))
        
        def test_get_local_metadata(self):
            data = get_local_metadata()
            self.assertTrue(isinstance(data, pd.DataFrame))
    
        def test_get_insee_local(self):  
    
            dep = get_geo_list('departements')
    
            variables = 'AGESCOL-SEXE-ETUD'
            dataset = 'GEO2019RP2011'
            # codegeo = ['91', '976']
            codegeos = list(dep.CODE)
            geo = 'DEP'
            data = get_insee_local(variables=variables,
                                   dataset=dataset, geo=geo, geocodes = codegeos)
    
            self.assertTrue(isinstance(data, pd.DataFrame))
    
        def test_get_map_link(self):
            map_file = get_map_link('communes')
            map = gpd.read_file(map_file)
            self.assertTrue(isinstance(map, gpd.geodataframe.GeoDataFrame))