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

import os

from pynsee.metadata.get_definition_list import get_definition_list
from pynsee.metadata.get_insee_definition import get_insee_definition
from pynsee.metadata.get_naf import get_naf

class TestFunction(TestCase):

    def test_get_definition_list(self):
        data = get_definition_list()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_insee_definition_(self):
        data = get_insee_definition(ids=['c1020', 'c1601'])
        self.assertTrue(isinstance(data, pd.DataFrame))
        
    def test_get_naf(self):
        test = True
        list_naf = ['A10', 'A21', 'A38', 'A64', 'A88', 'A129', 'A138']
        for naf in list_naf:
            data = get_naf(naf)
            test = test & isinstance(data, pd.DataFrame)
        self.assertTrue(test)