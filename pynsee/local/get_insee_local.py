# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_future_dev():
    print("!!! This function is still at an early development stage,\nchanges are likely in the future !!!")


def get_insee_local(variables, dataset, geo, geocodes):
    
    _warning_future_dev()
    
    from pynsee.utils._request_insee import _request_insee
    from pynsee.utils._paste import _paste
    
    from tqdm import trange
    import pandas as pd
    import numpy as np
    
#    variables = 'AGESCOL-SEXE-ETUD';dataset = 'GEO2019RP2011';geocodes = ['91','92', '976'];geo = 'DEP'
    
    
    list_data_all = []
    
    for cdg in trange(len(geocodes), desc = "Getting data"): 
        
        codegeo = geocodes[cdg]
        
        if type(variables) == list:
                variables = _paste(variables, collapse = '-')
                
        count_sep = variables.count('-')
        modalite = '.all' * (count_sep+1)
        
        link = 'https://api.insee.fr/donnees-locales/V0.1/donnees/'
        link = link + 'geo-{}@{}/{}-{}{}'.format(variables, dataset, geo, codegeo, modalite)
        
        request = _request_insee(api_url = link, file_format = 'application/json;charset=utf-8')
               
        try:           
                    
            data_request = request.json()
            
            #if 'Cellule' in list(data_request.keys()):
            Cellule = data_request['Cellule']
            Variable = data_request['Variable']
            Croisement = data_request['Croisement']
            Zone = data_request['Zone']
            
            dataset_version = Croisement['JeuDonnees']['@code']
            dataset_name = Croisement['JeuDonnees']['Source']
            data_date = Croisement['JeuDonnees']['Annee']
            geo_date = Zone['Millesime']['@annee']
            codegeo_label = Zone['Millesime']['Nccenr']
            
            list_data = []
            
            for i in range(len(Cellule)):
                dico = {**Cellule[i]['Zone'], **Cellule[i]['Mesure']}
                modalite = Cellule[i]['Modalite']
                
                for m in range(len(modalite)):
                    dico_added = {modalite[m]['@variable']: modalite[m]['@code']}
                    dico = {**dico, **dico_added}
                    
                dico['OBS_VALUE'] =  Cellule[i]['Valeur']
                df = pd.DataFrame(dico, index=[0])
                list_data.append(df)
                
            data = pd.concat(list_data)
                    
            for i in range(len(Variable)):
                df = pd.DataFrame(Variable[i]['Modalite'])
                var_name = Variable[i]['@code']
                df = df[['@code', 'Libelle']]
                df.columns = [var_name, var_name + '_label']
                data = data.merge(df, on = var_name, how = 'left')
            
            data = data.assign(DATASET_VERSION = dataset_version,
                               DATASET_NAME = dataset_name,
                               DATA_DATE = data_date,
                               GEO_DATE = geo_date,
                               CODEGEO_label = codegeo_label)
            
            data.rename(columns={'@codgeo':'CODEGEO',
                                 '@nivgeo':'NIVGEO',
                                 '@code':'UNIT',
                                 '$':'UNIT_label'}, inplace=True)
            
            data['OBS_VALUE'] = pd.to_numeric(data['OBS_VALUE'])
#            data['DATA_DATE'] = pd.to_numeric(data['DATA_DATE'])
#            data['GEO_DATE'] = pd.to_numeric(data['GEO_DATE'])
            list_data_all.append(data)
        except:
            data = pd.DataFrame({'CODEGEO':codegeo,'OBS_VALUE':np.nan},index=[0])
            list_data_all.append(data)
 
    data_final = pd.concat(list_data_all).reset_index(drop=True)
        
    return(data_final)
           