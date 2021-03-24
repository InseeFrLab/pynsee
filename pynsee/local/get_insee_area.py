# -*- coding: utf-8 -*-
#from functools import lru_cache
#
#@lru_cache(maxsize=None)
def get_insee_area(area_type, codeareas):
    
#    codeareas = ['1109']
#    area_type = 'zonesDEmploi2020'
    
    import pandas as pd    
    from tqdm import trange
    
    from pynsee.utils._request_insee import _request_insee
    from pynsee.local.get_area_list import get_area_list
    
    df_list = get_area_list(area_type)
    list_available_codeareas = df_list.code.to_list()

    if area_type == 'zonesDEmploi2020':
        type2 = 'zoneDEmploi2020'
    if area_type == 'airesDAttractionDesVilles2020':
        type2 = 'aireDAttractionDesVilles2020'
    if area_type == 'unitesUrbaines2020':
        type2 = 'uniteUrbaine2020'

    list_data = []    
    
    for c in trange(len(codeareas)):        
    
        if codeareas[c] in list_available_codeareas:
            api_url = 'https://api.insee.fr/metadonnees/V1/geo/'
            api_url = api_url  + type2 + '/' + codeareas[c] + '/descendants'
            request = _request_insee(api_url = api_url,  file_format = 'application/json')
            
            data = request.json()
            list_data_area = []
            for i in range(len(data)):
                df = pd.DataFrame(data[i], index=[0])
                list_data_area.append(df)
                
            data_area = pd.concat(list_data_area).reset_index(drop=True)
            
            ref_area_label = df_list.loc[df_list.code == codeareas[c]].intitule
            ref_area_label = ref_area_label.reset_index(drop=True)[0]
            
            data_area = data_area.assign(ref_area_code = codeareas[c],
                                         ref_area_label = ref_area_label)
            list_data.append(data_area)
        else:
            print('{} is not available in get_area_list({})'.format(codeareas[c], area_type))
   
    data_final = pd.concat(list_data)
    data_final = data_final.assign(area_type=area_type)
    return(data_final)
    