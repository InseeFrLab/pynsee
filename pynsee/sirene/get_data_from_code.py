# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from functools import lru_cache

from pynsee.utils._request_insee import _request_insee

@lru_cache(maxsize=None)
def _warning_get_data_from_code():
    print("!!! This function may return personal data,\n please check and comply with the legal framework relating to personal data protection !!!")

def get_data_from_code(*siren):
    """Get data about one or several companies from siren codes

    Notes:
        This function may return personal data, please check and comply with the legal framework relating to personal data protection

    Examples:
        >>> df = get_data_from_code("552081317")
    """    
    
    INSEE_api_sirene_siren = "https://api.insee.fr/entreprises/sirene/V3/siren"
#    INSEE_api_sirene_siret = "https://api.insee.fr/entreprises/sirene/V3/siret"
    
    list_data = []
    
    for code in siren:
        link = INSEE_api_sirene_siren + '/' + str(code)
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
    
    _warning_get_data_from_code()

    return(data_final)