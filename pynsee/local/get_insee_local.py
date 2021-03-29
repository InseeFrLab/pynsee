# -*- coding: utf-8 -*-

def get_insee_local(variables, dataset_version, nivgeo, geocodes):
    
    from pynsee.utils._get_insee_local_onegeo import _get_insee_local_onegeo
    
    from tqdm import trange
    import pandas as pd
    
#    variables = 'AGESCOL-SEXE-ETUD';dataset_version = 'GEO2019RP2011';geocodes = ['91','92', '976'];nivgeo = 'DEP'
      
    list_data_all = []
    
    for cdg in trange(len(geocodes), desc = "Getting data"): 
        
        codegeo = geocodes[cdg]
        
        df = _get_insee_local_onegeo(variables, dataset_version, nivgeo, codegeo)
        
        list_data_all.append(df)
 
    data_final = pd.concat(list_data_all).reset_index(drop=True)
        
    return(data_final)
           