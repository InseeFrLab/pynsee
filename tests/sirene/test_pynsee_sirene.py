
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
        df1 = get_data_sirene("?q=periode(denominationUniteLegale.phonetisation:sncf)&nombre=20")        
        df2 = get_data_sirene('?q=denominationUniteLegale.phonetisation:oto&nombre=20', kind='siret')
        df3 = get_data_sirene('?q=denominationUniteLegale.phonetisation:oto&nombre=20&champs=denominationUniteLegale', kind='siret')
        
        test = isinstance(df1, pd.DataFrame) & isinstance(df2, pd.DataFrame) & isinstance(df3, pd.DataFrame)
        self.assertTrue(test)