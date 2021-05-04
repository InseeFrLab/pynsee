# -*- coding: utf-8 -*-

# import re
import pandas as pd
#import sys, os
from functools import lru_cache
from tqdm import trange

from pynsee.utils._request_insee import _request_insee
from pynsee.metadata.get_activity_list import get_activity_list
from pynsee.metadata.get_insee_legal_entity import get_insee_legal_entity

@lru_cache(maxsize=None)
def get_data_sirene(query, kind = 'siren', clean=True,
                    activity=True, legal=True, only_alive=True):
    """Get data from any criteria-based query

    Args:
        query (str): query string

        kind (str, optional): kind of entitty: siren or siret. Defaults to 'siren'.

        clean (bool, optional): If True empty columns are removed. Defaults to True.
        
        activity (bool, optional): If True activity label is added. Defaults to True.

    Raises:
        ValueError: If kind is not equal to 'siret' or 'siren' an error is raised.
    """            
    INSEE_api_sirene_siren = "https://api.insee.fr/entreprises/sirene/V3"
    
    link = INSEE_api_sirene_siren + '/' + kind + query
    
    if kind == 'siren':        
        main_key = 'unitesLegales'
    elif kind == 'siret':
        main_key = 'etablissements'
    else:
        raise ValueError('!!! kind should be among : siren siret !!!')
    
    request = _request_insee(api_url = link, file_format = 'application/json;charset=utf-8')
    
    list_dataframe = []
    
    if request.status_code == 200:
    
        data_request = request.json()
        
        # main_key_list = [key for key in list(data_request.keys()) if key != "header"]
        # main_key = main_key_list[0]
        
        data = data_request[main_key]          
        
        for i in trange(len(data), desc='Getting data'):
            idata = data[i]
            
            key_list = [key for key in idata.keys() if type(idata[key]) is list]
            key_not_list = [key for key in idata.keys() if type(idata[key]) is not list]
            
            key_dict = [key for key in idata.keys() if type(idata[key]) is dict]
            key_not_list_dict = [key for key in key_not_list if type(idata[key]) is not dict]
                        
            data_from_list = []        
            for key in key_list:
                df = pd.DataFrame(idata[key])
                data_from_list.append(df)
            
            newdict = { key : idata[key] for key in key_not_list_dict }
            
            data_other0 = pd.DataFrame(newdict, index=[0])
            
            data_from_dict = []
            for key in key_dict:
                df = pd.DataFrame(idata[key], index=[0])
                data_from_dict.append(df)
                
            if len(data_from_list) !=0:
                data_from_list = pd.concat(data_from_list).reset_index(drop=True)
                
                list_data_other = []
                for i in range(len(data_from_list.index)):
                    list_data_other.append(data_other0)
                data_other = pd.concat(list_data_other).reset_index(drop=True)
                
                if len(data_from_dict) !=0:
                    data_dict0 = pd.concat(data_from_dict, axis=1)
                    list_data_dict = []
                    for i in range(len(data_from_list.index)):
                        list_data_dict.append(data_dict0)      
                    data_dict = pd.concat(list_data_dict).reset_index(drop=True)
                    data_final = pd.concat([data_other, data_dict, data_from_list], axis=1)
                else:
                    data_final = pd.concat([data_other, data_from_list], axis=1)

            else:
                if len(data_from_dict) !=0:
                    data_dict0 = pd.concat(data_from_dict, axis=1)
                    data_final =  pd.concat([data_other0, data_dict0], axis=1)
                else:
                    data_final = data_other0   
                     
            
            list_dataframe.append(data_final)
            
        data_final = pd.concat(list_dataframe)
                
        # add activity metadata
        if activity:
            naf5 = get_activity_list("NAF5")
            naf5 = naf5[["NAF5", "TITLE_NAF5_FR"]]
             
            if "activitePrincipaleUniteLegale" in data_final.columns:
               
                naf5_merge = naf5.rename(columns={"NAF5":"activitePrincipaleUniteLegale",
                                                  "TITLE_NAF5_FR":"activitePrincipaleUniteLegaleTitle"})
                data_final = data_final.merge(naf5_merge, on ="activitePrincipaleUniteLegale", how="left")
            
            if "activitePrincipaleEtablissement" in data_final.columns:
                
                naf5_merge = naf5.rename(columns={"NAF5":"activitePrincipaleEtablissement",
                                                  "TITLE_NAF5_FR":"activitePrincipaleEtablissementTitle"})
                data_final = data_final.merge(naf5_merge, on ="activitePrincipaleEtablissement", how="left")
            
                
        #remove companies which no longer exist
        if only_alive:
            if 'dateFin' in data_final.columns:
                data_final = data_final[data_final['dateFin'].isnull()]
        
        # add legal entities title
        if legal:
            if 'categorieJuridiqueUniteLegale' in data_final.columns:
                list_legal_code = data_final.categorieJuridiqueUniteLegale.unique()
                data_legal = get_insee_legal_entity(list_legal_code, print_err_msg=False)
                data_legal = data_legal[['code', 'title']]
                data_legal = data_legal.rename(columns={'code' : 'categorieJuridiqueUniteLegale',
                                                        'title' : 'categorieJuridiqueUniteLegaleTitle'})
                data_final = data_final.merge(data_legal, on = 'categorieJuridiqueUniteLegale', how='left')
                                
        # empty columns at the end
        list_all_na_col = [col for col in data_final.columns if all(pd.isna(data_final[col]))]
        list_first_col = [col for col in data_final.columns if col not in list_all_na_col]
        data_final = data_final[list_first_col + list_all_na_col]
        
        # change colummn order        
        if kind == 'siren' :
            first_col = ['siren', 'denominationUniteLegale' ,
                         'dateFin', 'dateDebut', 'categorieEntreprise',
                         'categorieJuridiqueUniteLegale', 'activitePrincipaleUniteLegale']
            
        if kind == 'siret' :            
            first_col = ['siren', 'nic' , 'siret', 'dateDebut', 'dateCreationEtablissement',
                         'dateCreationUniteLegale', 'dateFin',                          
                         'denominationUniteLegale', 'nomUniteLegale',
                         'prenomUsuelUniteLegale',
                         'categorieEntreprise',
                         'categorieJuridiqueUniteLegale',
                         'activitePrincipaleUniteLegale',
                         'activitePrincipaleEtablissement',
                         'numeroVoieEtablissement',
                         'typeVoieEtablissement',
                         'libelleVoieEtablissement', 'codePostalEtablissement',
                         'libelleCommuneEtablissement',  'codeCommuneEtablissement']
            
        if set(first_col).issubset(data_final.columns):
            other_col = [col for col in data_final if col not in first_col]
            data_final = data_final[first_col + other_col]
        
        # move columns title after columns containing values
        for var in ['categorieJuridiqueUniteLegale', 
                    'activitePrincipaleUniteLegale',
                    'activitePrincipaleEtablissement']:
            
            if var + 'Title' in data_final.columns:
                loc_var = data_final.columns.get_loc(var)
                col2insert = data_final[var + 'Title']
                data_final = data_final.drop([var+ 'Title'], axis = 1)
                data_final.insert(loc_var+1, var + 'Title', col2insert)
        
        if clean:
            data_final = data_final.dropna(axis=1, how='all')
            
        return(data_final)
    else:        
        print(request.text)
