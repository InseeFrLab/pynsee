# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% construction de la fonction get_metadata qui permet d'obtenir les metadatas d'un DS melodi

def get_metadata(ds_name: str,
                base_url_melodi: str = "https://api.insee.fr/melodi"):
     
    """
    
    Description
    ----------
    
    Get dataset metadata.
    
    Parameters
    ----------
    
    ds_name : dataset name
      
    base_url_melodi : API Melodi URL - default production URL : "https://api.insee.fr/melodi"
    
    Returns
    -------
    
    List dataset metadata.
    
    Examples
    --------
    
    metadata=pynsee.get_metadata(ds_name = "DS_POPULATIONS_REFERENCE")
    
    """
    
    url = f"{base_url_melodi}/catalog/{ds_name}"
    print(f"Request dataset: {url}")

    try:     
        #Requête melodi
        response = requests.get(url, timeout=30,headers=HEADERS)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes

        #Transformer en json
        dataset = response.json()

    #Gestion des erreurs réseau
    except requests.exceptions.HTTPError as e:
        status_code = (
        e.response.status_code if e.response is not None else "unknown")
        raise RuntimeError(f"HTTP Error {status_code}: The URL or resource might be incorrect:"f" {url}.")

    #API trop longue
    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. The server is taking too long to respond.")

    #Si json non valide
    except requests.exceptions.JSONDecodeError: 
        raise RuntimeError(f"The API did not return valid JSON. Check if the dataset name '{ds_name}' is correct (URL: {url}).")

    #Autres erreurs
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while requesting Melodi API: {e}")
        
    #Afficher les métadonnées du dataset
    for key, value in dataset.items():
        print("\n",key, ":\n", value)
        
    #Retourner le dictionnaire python
    return dataset

# %%

