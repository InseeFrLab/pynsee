# -*- coding: utf-8 -*-

import re
import pandas as pd
from pynsee.utils._request_insee import _request_insee

def get_data_sirene(query, kind = 'siren'):
            
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
        
        # main_key = [key for key in list(data_request.keys()) if key != "header"]
        # main_key = main_key[0]
        
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
        
        # empty columns at the end
        list_all_na_col = [col for col in data_final.columns if all(pd.isna(data_final[col]))]
        list_first_col = [col for col in data_final.columns if col not in list_all_na_col]
        data_final = data_final[list_first_col + list_all_na_col]
        
        return(data_final)
    else:
        print(request.text)
         # m = re.search("ams\\:description\\>.*\\<\\/ams\\:description", results.text)
#                    if m:
#                        found = m.group(0)
#                        found2 = found.replace("description", "").replace("ams", "")
#                        print(found2)
