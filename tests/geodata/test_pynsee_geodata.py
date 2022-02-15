# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

from unittest import TestCase
import pandas as pd
import sys

from shapely.geometry import Point, Polygon, MultiPolygon, MultiLineString, MultiPoint

from pynsee.geodata.get_geodata_list import get_geodata_list
from pynsee.geodata.get_geodata import get_geodata

from pynsee.geodata.GeoDataframe import GeoDataframe

class TestFunction(TestCase):

    version_3_7 = (sys.version_info[0] == 3) & (sys.version_info[1] == 7)

    if version_3_7:
        def test_get_geodata_short(self):
            df = get_geodata_list(update=True)
            self.assertTrue(isinstance(df, pd.DataFrame))

            ids = df.Identifier.to_list()

            list_geom_type = []

            data = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:commune', update=True) 
            self.assertTrue(isinstance(data, GeoDataframe))
            geo = data.get_geom()
            self.assertTrue(isinstance(geo, MultiPolygon))

            dep29 = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:departement', update=True)
            self.assertTrue(isinstance(dep29, GeoDataframe))
            geo29 = dep29.get_geom()
            self.assertTrue(isinstance(geo29, MultiPolygon))

            com29 = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:commune', update=True, polygon=geo29) 
            self.assertTrue(isinstance(com29, GeoDataframe))
            geocom29 = data.get_geom()
            self.assertTrue(isinstance(geocom29, MultiPolygon))

            data = get_geodata(id='test', update=True) 
            self.assertTrue(isinstance(data, pd.DataFrame))
        
        

    if False:

        def test_get_geodata_all(self):
            df = get_geodata_list(update=True)
            ids = df.Identifier.to_list()

            list_geom_type = []
            # ident = 'LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:epci'
            # ident = 'ADMINEXPRESS-COG-CARTO.LATEST:commune'

            data = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:commune', update=True) 
            list_geom_type += [type(data.get_geom())]

            dep29 = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:departement', update=True)
            dep29 = dep29[dep29["insee_dep"] == "29"]
            geodep29 = dep29.get_geom()   
            list_geom_type += [type(geodep29)]         
        
            for id in range(len(ids)):
                
                ident = ids[id]
                print("%s %s" % (id, ident))

                data = get_geodata(id=ident, update=True, polygon=geodep29)

                if type(data) == GeoDataframe:    
                    geom = data.get_geom()
                    list_geom_type += [type(geom)]

            print(list_geom_type)            
            
            test = all([typegeo in [Polygon, MultiPolygon, MultiLineString, MultiPoint] for typegeo in list_geom_type])

            self.assertTrue(test)
