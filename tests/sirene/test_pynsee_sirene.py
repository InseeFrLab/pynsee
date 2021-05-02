
from unittest import TestCase
from pandas import pandas as pd

from pynsee.sirene.get_data_from_code import get_data_from_code
from pynsee.sirene.get_data_from_pattern import get_data_from_pattern
from pynsee.sirene.get_data_sirene import get_data_sirene

class TestFunction(TestCase):

    def test_get_data_from_code(self):  
        df1 = get_data_from_code("552081317", "808332670")     
        df2 = get_data_from_code("817899438")
        test = isinstance(df1, pd.DataFrame) & isinstance(df2, pd.DataFrame)
        self.assertTrue(test)

    def test_get_data_from_pattern(self):  
        df1 = get_data_from_pattern("sncf")  
        df2 = get_data_from_pattern("sncf", kind="siret")
        df3 = get_data_from_pattern(variable="libelleCommuneEtablissement",
                                    pattern="montrouge", kind="siret")
        
        df4 = get_data_from_pattern(variable = ["activitePrincipaleUniteLegale", 
                                                "codePostalEtablissement"],
                                    kind = "siret",
                                    pattern = ["86.10Z", "75*"], number = 1000000)
        
        test = isinstance(df1, pd.DataFrame) &
                isinstance(df2, pd.DataFrame) &
                isinstance(df3, pd.DataFrame) &
                isinstance(df4, pd.DataFrame)
        
        self.assertTrue(test)
    
    def test_get_data_sirene(self):  
        
        list_query_siren = ["?q=periode(denominationUniteLegale.phonetisation:sncf)&nombre=20",
                 '?q=sigleUniteLegale:???',
                 '?q=periode(activitePrincipaleUniteLegale:86.10Z)&nombre=1000000']
        
        test = True
        for q in list_query_siren:
            df = get_data_sirene(q, kind= 'siren')
            test = test & isinstance(df, pd.DataFrame)

        list_query_siret =['?q=denominationUniteLegale.phonetisation:oto&nombre=20&champs=denominationUniteLegale', 
                '?q=prenom1UniteLegale:hadrien AND nomUniteLegale:leclerc',
                '?q=prenom1UniteLegale.phonetisation:hadrien AND nomUniteLegale.phonetisation:leclerc',
                '?q=activitePrincipaleUniteLegale:8*',
                '?q=activitePrincipaleUniteLegale:86.10Z&nombre=1000000', 
                '?q=activitePrincipaleUniteLegale:86.10Z AND codePostalEtablissement:75*&nombre=5000', 
                '?q=denominationUniteLegale.phonetisation:oto&nombre=20']

        for q in list_query_siret:
            df = get_data_sirene(q, kind= 'siret')
            test = test & isinstance(df, pd.DataFrame)
                
        self.assertTrue(test)