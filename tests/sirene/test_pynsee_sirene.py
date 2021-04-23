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

from pynsee.sirene.get_data_from_code import get_data_from_code
from pynsee.sirene.get_data_from_pattern import get_data_from_pattern
from pynsee.sirene.get_data_sirene import get_data_sirene

class TestFunction(TestCase):

    def test_get_data_from_code(self):  
        df = get_data_from_code("552081317", "808332670")        
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_data_from_pattern(self):  
        df = get_data_from_pattern("sncf")        
        self.assertTrue(isinstance(df, pd.DataFrame))
    
    def test_get_data_sirene(self):  
        df = get_data_sirene("sncf")        
        self.assertTrue(isinstance(df, pd.DataFrame))