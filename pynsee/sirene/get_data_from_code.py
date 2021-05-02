# -*- coding: utf-8 -*-

#siren = ["552081317"]
#code = "552081317"

def get_data_from_code(*siren):
    """Get data about one or several companies from siren codes

    Examples:
        >>> df = get_data_from_code("552081317")
    """    
    import pandas as pd
    from pynsee.utils._request_insee import _request_insee
    
    INSEE_api_sirene_siren = "https://api.insee.fr/entreprises/sirene/V3/siren"
#    INSEE_api_sirene_siret = "https://api.insee.fr/entreprises/sirene/V3/siret"
    
    list_data = []
    
    for code in siren:
        link = INSEE_api_sirene_siren + '/' + code
        request = _request_insee(api_url = link, file_format = 'application/json;charset=utf-8')

        data_request = request.json()
        
        data = data_request['uniteLegale']
        key_list = [key for key in data.keys() if type(data[key]) is list]
        
        data_period = pd.DataFrame(data['periodesUniteLegale'])
        
        for key in key_list:
            del data[key]
        
        data_other0 = pd.DataFrame(data, index=[0])
        
        list_data_other = []
        for i in range(len(data_period.index)):
            list_data_other.append(data_other0)
        data_other = pd.concat(list_data_other).reset_index(drop=True)
        
        data_final = pd.concat([data_other, data_period], axis=1)
        list_data.append(data_final)
    
    data_final = pd.concat(list_data).reset_index(drop=True)
    
    return(data_final)