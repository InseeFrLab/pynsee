# -*- coding: utf-8 -*-

def get_definition_list():
    
    from pynsee.utils._request_insee import _request_insee
    
    import pandas as pd
    
    link = 'https://api.insee.fr/metadonnees/V1/concepts/definitions'
    
    request = _request_insee(api_url = link, file_format = 'application/json')
    
    data_request = request.json()    
    
    list_data = []
    
    for i in range(len(data_request)):      
        df = pd.DataFrame(data_request[i], index=[0])
        df = df[['id', 'uri', 'intitule']]
        list_data.append(df)
        
    data = pd.concat(list_data)            
     
    return(data)           