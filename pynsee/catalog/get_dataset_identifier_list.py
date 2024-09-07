import os
import requests
import pandas as pd

def get_dataset_identifier_list():
    
    url = "https://api.insee.fr/melodi/catalog/all"
    
    r = requests.get(url)
    
    list_dict = r.json()
    
    list_data_dict = []
    
    for i in range(len(list_dict)):
        dico = {}
        for k, v in list_dict[i].items():
            if type(v) == list:
                for d2 in v:  
                    if type(d2) == dict:
                        if all(j in d2.keys() for j in ['lang', 'content']):
                            dico[k + "_" + d2['lang']] = d2['content']                   
            elif type(v) == str:
                dico[k] = v
        list_data_dict += [dico]
            
    return pd.DataFrame(list_data_dict)

# url = "https://api.insee.fr/melodi/catalog/ids"

# r = requests.get(url)

# list_dict = r.json()
# list_dict

# requete_dataset = requests.get("https://api.insee.fr/melodi/data/DS_RP_POPULATION_PRINC").json()
# requete_dataset

# url = "https://api.insee.fr/melodi/geo/groupes/all"

# r = requests.get(url)
# [for d['identifier'] for d in r.json()]

# url = "https://api.insee.fr/melodi/geo/groupes/ids"

# r = requests.get(url)
# r.json()

# url = "https://api.insee.fr/melodi/geo/groupes/FM"

# r = requests.get(url)
# r.json()