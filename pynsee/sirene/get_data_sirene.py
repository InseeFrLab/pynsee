# -*- coding: utf-8 -*-

def get_data_sirene(query, kind = 'siren'):
    
    import pandas as pd
    from pynsee.utils._request_insee import _request_insee
        
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
        
        data = data_request[main_key]          
        
        for i in range(len(data)):
            idata = data[i]
            
            key_list = [key for key in idata.keys() if type(idata[key]) is list]
            key_not_list = [key for key in idata.keys() if type(idata[key]) is not list]
            
            data_from_list = []        
            for key in key_list:
                df = pd.DataFrame(idata[key])
                data_from_list.append(df)
                
            data_from_list = pd.concat(data_from_list).reset_index(drop=True)
            
            newdict = { key : idata[key] for key in key_not_list }
            
            data_other0 = pd.DataFrame(newdict, index=[0])
            
            list_data_other = []
            for i in range(len(data_from_list.index)):
                list_data_other.append(data_other0)
                
            data_other = pd.concat(list_data_other).reset_index(drop=True)
            
            data_final = pd.concat([data_other, data_from_list], axis=1)
            list_dataframe.append(data_final)
            
        data_final = pd.concat(list_dataframe)
        
        return(data_final)
    else:
        print(request.text)