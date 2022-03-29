import os
import sys
import pandas as pd

from pynsee.utils._request_insee import _request_insee
from pynsee.sirene._make_dataframe_from_dict import _make_dataframe_from_dict

def get_relatives(siret):
    
    if type(siret) == str:
        siret = [siret]
    
    if type(siret) != list:
        raise ValueError('!!! siret should be a list or a str !!!')
        
    types = ['siretEtablissementPredecesseur', 'siretEtablissementSuccesseur']
    list_df = []
    
    for s in range(len(siret)):
        for i in range(len(types)):
            
            criteria = types[i] + ':' + siret[s]
            query = f'https://api.insee.fr/entreprises/sirene/V3/siret/liensSuccession?q={criteria}'
            try:
                sys.stdout = open(os.devnull, 'w')
                result = _request_insee(
                                api_url=query, file_format='application/json;charset=utf-8')
                json = result.json()
                sys.stdout = sys.__stdout__
            except:
                pass
            else:
                list_df += [_make_dataframe_from_dict(json)]    
    
    if len(list_df) > 0:
        df = pd.concat(list_df).reset_index(drop=True)
        return df
    else:
        raise ValueError('Neither parent nor child entities were found for any entity')
       
    


    