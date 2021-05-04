# -*- coding: utf-8 -*-

# import re
import pandas as pd
from pynsee.utils._request_insee import _request_insee
from pynsee.metadata.get_activity_list import get_activity_list
from pynsee.metadata.get_insee_legal_entity import get_insee_legal_entity

def get_data_sirene(query, kind = 'siren', clean=True, activity=True, legal=True):
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
        
        for i in range(len(data)):
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
        
        if clean:
            data_final = data_final.dropna(axis=1, how='all')
        
        # add activity metadata
        if activity:
            if "activitePrincipaleUniteLegale" in data_final.columns:
                data_final["NAF5"] = data_final["activitePrincipaleUniteLegale"]
                naf5 = get_activity_list("NAF5")
                naf5 = naf5[["NAF5", "TITLE_NAF5_FR"]]
                data_final = data_final.merge(naf5, on ="NAF5", how="left")
        
        # add legal entities title
        if legal:
            if 'categorieJuridiqueUniteLegale' in data_final.columns:
                data_legal = get_insee_legal_entity(data_final.categorieJuridiqueUniteLegale.unique())
                data_legal = data_legal[['code', 'title']]
                data_legal = data_legal.rename(columns={'code' : 'categorieJuridiqueUniteLegale',
                                                        'title' : 'categorieJuridiqueUniteLegaleTitle'})
                data_final = data_final.merge(data_legal, on = 'categorieJuridiqueUniteLegale', how='left')
        
        # empty columns at the end
        list_all_na_col = [col for col in data_final.columns if all(pd.isna(data_final[col]))]
        list_first_col = [col for col in data_final.columns if col not in list_all_na_col]
        data_final = data_final[list_first_col + list_all_na_col]
        
        return(data_final)
    else:
        print("Query : %s" % link)
        print(request.text)
