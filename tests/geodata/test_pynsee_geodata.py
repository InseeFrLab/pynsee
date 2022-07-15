# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

from unittest import TestCase
import pandas as pd
import sys
import requests

from shapely.geometry import Polygon, MultiPolygon, MultiLineString, MultiPoint, Point

from pynsee.geodata.get_geodata_list import get_geodata_list
from pynsee.geodata.get_geodata import get_geodata
from pynsee.geodata._get_geodata import _get_geodata
from pynsee.geodata._get_bbox_list import _get_bbox_list
from pynsee.geodata.GeoFrDataFrame import GeoFrDataFrame
from pynsee.geodata._get_data_with_bbox import _get_data_with_bbox, _set_global_var

# manual commands for testing only on geodata module
# coverage run -m unittest tests/geodata/test_pynsee_geodata.py
# coverage report --omit=*/utils/*,*/macrodata/*,*/localdata/*,*/download/*,*/sirene/*,*/metadata/* -m

class TestFunction(TestCase):

    version_3_7 = (sys.version_info[0] == 3) & (sys.version_info[1] == 7)

    if version_3_7 is False:
        def test_get_geodata_short(self):
            
            global session
            session = requests.Session()
            list_bbox = (-2, 43.0, 6.0, 44.5)
            for crs in ["EPSG:4326"]:
                link= f"https://wxs.ign.fr/administratif/geoportail/wfs?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAME=ADMINEXPRESS-COG-CARTO.LATEST:commune&srsName={crs}&OUTPUTFORMAT=application/json&COUNT=1000"
                data = _get_data_with_bbox(link, list_bbox, crsPolygon=crs)
                self.assertTrue(isinstance(data, pd.DataFrame))   
            
            square = [Point(0, 0),
                      Point(0, 0),   
                      Point(0, 0),   
                      Point(0, 0)] 
                
            poly_bbox = Polygon([[p.x, p.y] for p in square])
            df = _get_geodata(id = 'ADMINEXPRESS-COG-CARTO.LATEST:commune', polygon = poly_bbox, update=True)
            self.assertTrue(isinstance(df, pd.DataFrame))   
            
            _set_global_var(args=[link, list_bbox, session, "EPSG:4326"])
            
            df = get_geodata_list(update=True)
            self.assertTrue(isinstance(df, pd.DataFrame))
            
            chflieu = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:chflieu_commune', update=True) 
            self.assertTrue(isinstance(chflieu, GeoFrDataFrame))
            geo = chflieu.get_geom()
            self.assertTrue(isinstance(geo, MultiPoint))
            geo_chflieut = chflieu.translate().zoom().get_geom()
            self.assertTrue(isinstance(geo_chflieut, MultiPoint))            

            com = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:commune', update=True) 
            self.assertTrue(isinstance(com, GeoFrDataFrame))
            geo = com.get_geom()
            self.assertTrue(isinstance(geo, MultiPolygon))

            # query with polygon and crs 4326
            dep29 = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:departement', update=True, crs="EPSG:4326")
            dep29 = dep29[dep29["insee_dep"] == "29"]
            self.assertTrue(isinstance(dep29, GeoFrDataFrame))
            geo29 = dep29.get_geom()
            self.assertTrue(isinstance(geo29, MultiPolygon))

            com29 = _get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:commune', update=True, polygon=geo29, crsPolygon="EPSG:4326") 
            self.assertTrue(isinstance(com29, pd.DataFrame))
           
            # query with polygon and crs 3857
            dep29 = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:departement', update=True, crs="EPSG:3857")
            dep29 = dep29[dep29["insee_dep"] == "29"]
            self.assertTrue(isinstance(dep29, GeoFrDataFrame))

            geo29 = dep29.get_geom()
            self.assertTrue(isinstance(geo29, MultiPolygon))
            com29 = _get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:commune', update=True, polygon=geo29, crsPolygon="EPSG:3857") 
            self.assertTrue(isinstance(com29, pd.DataFrame))            

            ovdep = com.translate().zoom()
            self.assertTrue(isinstance(ovdep, GeoFrDataFrame))
            geo_ovdep = ovdep.get_geom()
            self.assertTrue(isinstance(geo_ovdep, MultiPolygon))
                    
            #test _add_insee_dep_from_geodata
            epci = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:epci', update=True) 
            self.assertTrue(isinstance(epci, GeoFrDataFrame))            
            epcit = epci.translate().zoom()
            self.assertTrue(isinstance(epcit, GeoFrDataFrame))
            geo_epcit = epcit.get_geom()
            self.assertTrue(isinstance(geo_epcit, MultiPolygon))
            
            # test _add_insee_dep_region
            reg = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:region', update=True) 
            self.assertTrue(isinstance(reg, GeoFrDataFrame))            
            regt = reg.translate().zoom()
            self.assertTrue(isinstance(regt, GeoFrDataFrame))
            geo_regt = regt.get_geom()
            self.assertTrue(isinstance(geo_regt, MultiPolygon))  

            dep = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:departement', crs="EPSG:4326")
            dep13 = dep[dep["insee_dep"] == "13"]
            geo13 = dep13.get_geom()          
               
            bbox = _get_bbox_list(polygon=geo13, update=True, crsPolygon="EPSG:4326")
            self.assertTrue(isinstance(bbox, list))
            bbox = _get_bbox_list(polygon=geo13)
            self.assertTrue(isinstance(bbox, list))

            dep = get_geodata(id='ADMINEXPRESS-COG-CARTO.LATEST:departement', crs="EPSG:3857")
            dep13 = dep[dep["insee_dep"] == "13"]
            geo13 = dep13.get_geom()          
               
            bbox = _get_bbox_list(polygon=geo13, update=True, crsPolygon="EPSG:3857")
            self.assertTrue(isinstance(bbox, list))
            
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

                if type(data) == GeoFrDataFrame:    
                    geom = data.get_geom()
                    list_geom_type += [type(geom)]

            print(list_geom_type)            
            
            test = all([typegeo in [Polygon, MultiPolygon, MultiLineString, MultiPoint] for typegeo in list_geom_type])

            self.assertTrue(test)
