# Copyright : INSEE, 2021

from unittest import TestCase
from pandas import pandas as pd
import sys

from pynsee.sirene.get_data_from_code import get_data_from_code
from pynsee.sirene.search_sirene import search_sirene
from pynsee.sirene._request_sirene import _request_sirene

class TestFunction(TestCase):

    def test_get_data_from_code(self):  
        df1 = get_data_from_code("552081317", "808332670")     
        df2 = get_data_from_code("817899438")
        test = isinstance(df1, pd.DataFrame) & isinstance(df2, pd.DataFrame)
        self.assertTrue(test)

    version_3_7 = (sys.version_info[0]==3) & (sys.version_info[1]==7)
    
    if version_3_7:

        def test_search_sirene(self):  
            
            test = True

            df = search_sirene(variable = ["activitePrincipaleUniteLegale", 
                                                    "codePostalEtablissement"],
                                        pattern = ["86.10Z", "75*"], kind = "siret")
            test = test & isinstance(df, pd.DataFrame)

            df = search_sirene(variable = ["libelleCommuneEtablissement",
                                        'denominationUniteLegale'],
                            pattern = ["igny", 'pizza'], 
                            phonetic_firstvar=True,
                            kind = "siret")
            test = test & isinstance(df, pd.DataFrame)

            #mix of variable with and without history on siren
            df = search_sirene(variable=["denominationUniteLegale",
                                       'categorieJuridiqueUniteLegale', 
                                       'categorieEntreprise'],                                     
                                        pattern=["sncf", '9220', 'PME'], kind="siren")
            test = test & isinstance(df, pd.DataFrame)

            #input as string and not list
            df = search_sirene(variable = 'libelleCommuneEtablissement',
                                         pattern= "montrouge", kind="siret")
            test = test & isinstance(df, pd.DataFrame)                        

            
            df = search_sirene(variable = ["denominationUniteLegale", 'categorieEntreprise'],
                                    pattern = ["Pernod Ricard", 'GE'], 
                                    phonetic_firstvar=True,
                                    kind = "siren")
            test = test & isinstance(df, pd.DataFrame)

            df = search_sirene(variable = ["denominationUniteLegale",
                                                 'categorieEntreprise',
                                                 'categorieJuridiqueUniteLegale'],
                                    pattern = ["Pernod Ricard", 'GE', '5710'], 
                                    kind = "siren")
            test = test & isinstance(df, pd.DataFrame)

            df = search_sirene(variable = ["denominationUniteLegale"],
                                    pattern = ["Pernod Ricard"], 
                                    kind = "siret")
            test = test & isinstance(df, pd.DataFrame)

            
            df = search_sirene(variable = ['denominationUniteLegale'],
                                pattern = ['tabac'], 
                                number = 2500,
                                kind = "siret")

            test = test & isinstance(df, pd.DataFrame)
                        
            self.assertTrue(test)



        def test_request_sirene(self):  
            
            list_query_siren = ["?q=periode(denominationUniteLegale.phonetisation:sncf)&nombre=20",
                    '?q=sigleUniteLegale:???',
                    '?q=periode(activitePrincipaleUniteLegale:86.10Z)&nombre=1000000']
            
            test = True
            for q in list_query_siren:
                df = _request_sirene(q, kind= 'siren')
                test = test & isinstance(df, pd.DataFrame)

            list_query_siret =['?q=denominationUniteLegale.phonetisation:oto&nombre=20&champs=denominationUniteLegale', 
                    '?q=prenom1UniteLegale:hadrien AND nomUniteLegale:leclerc',
                    '?q=prenom1UniteLegale.phonetisation:hadrien AND nomUniteLegale.phonetisation:leclerc',
                    '?q=activitePrincipaleUniteLegale:8*',
                    '?q=activitePrincipaleUniteLegale:86.10Z&nombre=1000000', 
                    '?q=activitePrincipaleUniteLegale:86.10Z AND codePostalEtablissement:75*&nombre=5000', 
                    '?q=denominationUniteLegale.phonetisation:oto&nombre=20']

            for q in list_query_siret:
                df = _request_sirene(q, kind= 'siret')
                test = test & isinstance(df, pd.DataFrame)            
            
            q = '?q=denominationUniteLegale.phonetisation:Pernod OR denominationUniteLegale.phonetisation:Ricard'
            df = _request_sirene(q, kind= 'siret')
            test = test & isinstance(df, pd.DataFrame)  

            q = '?q=periode(denominationUniteLegale.phonetisation:Dassault) OR periode(denominationUniteLegale.phonetisation:Système) AND categorieEntreprise:GE'
            df = _request_sirene(q, kind= 'siren')
            test = test & isinstance(df, pd.DataFrame)  
                    
            self.assertTrue(test)