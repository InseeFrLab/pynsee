# -*- coding: utf-8 -*-

def _get_insee_local(variables, dataset, codegeo, geo):
    
    from pynsee.utils._request_insee import _request_insee
    from pynsee.utils._paste import _paste
    
    import tempfile
    import xml.etree.ElementTree as ET
    import pandas as pd
    import os
    
#    variables = 'AGESCOL-SEXE-ETUD'
#    dataset = 'GEO2019RP2011'
#    codegeo = '91'
#    geo = 'DEP'
    
    if type(variables) == list:
        variables = _paste(variables, collapse = '-')
        
    count_sep = variables.count('-')
    modalite = '.all' * (count_sep+1)
    
    link = 'https://api.insee.fr/donnees-locales/V0.1/donnees/'
    link = link + 'geo-{}@{}/{}-{}{}'.format(variables, dataset, geo, codegeo, modalite)
    
    request = _request_insee(api_url = link)
    
    dirpath = tempfile.mkdtemp()
    
    file = dirpath + '\\data_file'
    
    with open(file, 'wb') as f:
        f.write(request.content)
    
    root = ET.parse(file).getroot()
    
    if os.path.exists(file):
        os.remove(file)
        
    list_data = []
    
    for i in range(len(root)):
#        print(i)
        if root[i].tag == 'Cellule':
            dict = {}
            for j in range(len(root[i])):
                
                if root[i][j].tag == 'Zone':
                    dict = {**dict, **root[i][j].attrib}
                    
                if root[i][j].tag == 'Modalite':
                    values = list(root[i][j].attrib.values())
                    dict[values[1]] = values[0]
                
                if root[i][j].tag == 'Valeur':
                    dict['value'] = root[i][j].text
                
                if root[i][j].tag == 'Mesure':
                    dict['measure'] = list(root[i][j].attrib.values())[0]
                    dict['measure_label'] = root[i][j].text
                
            list_data.append(pd.DataFrame(dict, index=[0]))
    
   
    data = pd.concat(list_data)
    data = data.assign(dataset = dataset)
     
    return(data)
           