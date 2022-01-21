# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

from unittest import TestCase
import pandas as pd
import sys

from shapely.geometry import Point, Polygon, MultiPolygon, MultiLineString, MultiPoint

from pynsee.geodata.get_geodata_list import get_geodata_list
from pynsee.geodata.get_geodata import get_geodata
class TestFunction(TestCase):

    def test_get_geodata_list(self):
        df = get_geodata_list()
        self.assertTrue(isinstance(df, pd.DataFrame))
    
    def test_get_geodata(self):
        df = get_geodata_list(update=True)
        ids = df.Identifier.to_list()

        list_geom_type = []
        # ident = 'LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:epci'

        for id in range(len(ids)):
            
            ident = ids[id]
            print("%s %s" % (id, ident))

            data = get_geodata(id=ident, update=True)
            
            geom = data.get_geom()
            list_geom_type += [type(geom)]

        print(list_geom_type)            
        test = all([typegeo in [Polygon, MultiPolygon, MultiLineString, MultiPoint] for typegeo in list_geom_type])

        self.assertTrue(test)