# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests
import pandas as pd
import json

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% création de la fonction get_data qui permet d'interroger l'API melodi via URL

def get_data(url: str) -> pd.DataFrame:
    
    """
    
    Description
    ----------
    
    Get Melodi data by URL.
    URL parameter can be copied/pasted from explorer https://catalogue-donnees.insee.fr.

    Parameters
    ----------
    
    url : URL API data Melodi - Start by "https://api.insee.fr/melodi/data/..."
    
    Returns
    -------
    
    DataFrame with data.
    
    Examples
    --------
    
    data=pynsee.get_data("https://api.insee.fr/melodi/data/DS_POPULATIONS_REFERENCE?POPREF_MEASURE=PMUN&GEO=FRANCE-F")
    
    data.info()  
    data.head()
    """
    
    #Pour gérer le cas où on met une url sans filtre => ajouter ? à la fin
    if "?" not in url:
        url=url+"?"
          
    #Construction de l'URL pour obtenir uniquement le nombre total de résultats (sans charger les données)
    request_count_url = f"{url}&totalCount=TRUE&maxResult=0"

    #Construction de l'URL pour récupérer les données complètes (jusqu’à 100 000 lignes)
    request_url = f"{url}&idTerritoire=TRUE&maxResult=100000"
    
    #Affiche l'URL utilisée pour compter les lignes
    print(f"Total count request : {request_count_url}")

    try:   

        #Envoie la requête HTTP GET pour obtenir le nombre total d'observations
        response_count = requests.get(request_count_url, stream=True, timeout=30,headers=HEADERS)
        response_count.raise_for_status()  # Raises an exception for 4xx/5xx status codes

        #Envoie de la requête HTTP GET pour obtenir les données
        response_data = requests.get(request_url, stream=True, timeout=30,headers=HEADERS)
        response_data.raise_for_status()  # Raises an exception for 4xx/5xx status codes
            
        #Permet d'accéder au contenu de la requête
        response_data_content = response_data.content
    
    #Gestion des erreurs réseau
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        raise RuntimeError(f"HTTP Error {status_code}: The URL or resource might be incorrect: {url}.")
    
    #API trop longue
    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. The server is taking too long to respond.")
        
    #Autres erreurs
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while requesting Mélodi API: {e}")
            
    #Conversion de la réponse JSON en dictionnaire Python
    data_count = response_count.json()

    #Extraction du nombre d'observations depuis la réponse
    count = data_count["paging"]["count"]

    #Affiche le nombre de lignes obtenues, avec formatage des milliers
    print(f"Number of lines : {count:,}")

        
    #Si aucune donnée n’est retournée, on arrête le programme avec une erreur explicite
    if count == 0:
        raise ValueError(f"No result for request {url}")
        
    #Si le nombre dépasse 100 000, on arrête également avec un message explicite
    elif count > 100000:
        raise ValueError("Request over 100,000 lines not supported yet,\n"
                             "please filter your request or use get_all_data")        

    #Transformer en json
    response_data_content_json = json.loads(response_data_content)

    #Récupérer les observations du json qui contient dimension + attribut + mesure
    observations = response_data_content_json['observations']

    #Initialisation du jeu de données que l'on aura en sortie de la fonction
    data = []

    #Boucle de lecture des observations dans le json 
    for obs in observations:
        row = {}

        row.update(obs.get("dimensions", {})) # ajouter la dimension à la ligne si dimension existe
        row.update(obs.get("attributes", {})) # ajouter les attributs à la ligne si attributs existe

        measures = obs.get("measures", {}).get("OBS_VALUE_NIVEAU", {}) # récupérer la mesure melodi
        row["OBS_VALUE"] = measures.get("value") # ajouter la valeur associée à la mesure

        data.append(row) # ajouter la ligne "row" à la liste "data"
            
    #Transformer data en type dataframe
    data=pd.DataFrame(data)

    #Renommer OBS_VALUE_NIVEAU en OBS_VALUE
    data = data.rename(columns={"OBS_VALUE_NIVEAU": "OBS_VALUE"})

    #Cas où il y a la variable GEO dans le jeu de donnée
    if "GEO" in data.columns:
        #Reconstruire les variables GEO_REF, GEO_OBJECT et GEO à partir de la variable GEO
        data['GEO_REF']=data['GEO'].str.split("-").str.get(0)
        data['GEO_OBJECT']=data['GEO'].str.split("-").str.get(1)
        data['GEO']=data['GEO'].str.split("-").str.get(2)

        #Mettre certaines colonnes en premiers
        premieres_colonnes = ['GEO_REF', 'GEO_OBJECT','GEO','TIME_PERIOD']
        autres_cols = [col 
                   for col in data.columns
                       if col not in premieres_colonnes]

        nouvel_ordre = premieres_colonnes + autres_cols

        #Trier les colonnes de data
        data=data[nouvel_ordre]
    
    #Cas où il n'y a pas la variable GEO dans le jeu de donnée
    elif "GEO" not in data.columns:

        #Mettre certaines colonnes en premiers
        premieres_colonnes = ['TIME_PERIOD']
        autres_cols = [col 
                   for col in data.columns
                       if col not in premieres_colonnes]

        nouvel_ordre = premieres_colonnes + autres_cols

        #Trier les colonnes de data
        data=data[nouvel_ordre]
        
    #Retourne le DataFrame final prêt à être utilisé
    return data


# %%
