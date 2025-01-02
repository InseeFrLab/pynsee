import os
import requests
import pandas as pd

def get_dataset_identifier_list():
    
    url = "https://api.insee.fr/melodi/catalog/all"

    r = requests.get(url)
    
    list_dict = r.json()
    
    list_data_dict = []
    list_product_dict = []
    
    for i in range(len(list_dict)):
        dico = {}
        for k, v in list_dict[i].items():
            if type(v) == list:
                if all([type(j) == str for j in v]):
                    dico[k] = ", ".join(v)
                for d2 in v:  
                    if type(d2) == dict:
                        if all(j in d2.keys() for j in ['lang', 'content']):
                            dico[k + "_" + d2['lang']] = d2['content']                   
            elif type(v) == str:
                dico[k] = v
                
        list_data_dict += [dico]
        
        if 'product' in list_dict[i].keys():
            if type(list_dict[i]["product"]) == list:
                for p in list_dict[i]["product"]:
                    if type(p) == dict:
                        product = p
                        product["identifier"] = list_dict[i]["identifier"]
                        list_product_dict += [product]
                        
    meta = pd.DataFrame(list_data_dict)
    products = pd.DataFrame(list_product_dict)     
    list_col_dropped = [c for c in products.columns if (c in meta.columns) and (c != "identifier")]
    meta2 = meta.drop(columns = list_col_dropped)

    dataset = (products
               .merge(meta2, on = "identifier", how="left")
               .rename(columns = {"identifier": "dataset_identifier"})          
              )
            
    return dataset

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