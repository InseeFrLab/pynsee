# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests
import pandas as pd

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% construction de la fonction get_range_geo
def get_range_geo(ds_name: str,
    base_url_melodi: str = "https://api.insee.fr/melodi",
    lang: str = "fr")-> pd.DataFrame:
    
    """
    
    Description
    ----------
    
    Get dataset's geography : codes and labels.
    Retrieves the list of geo dimensions and all their possible values (codes and human-readable labels) for a given dataset.
    
    Parameters
    ----------
    
    ds_name : dataset name
    
    base_url_melodi : API Melodi URL - default prod
    
    lang : french (fr) or english (en) labels - default french ("fr")
    
    Returns
    -------
    
    DataFrame with columns `GEO_REF`, `GEO_OBJECT`, `GEO_OBJECT_LABEL`, `GEO`, `GEO_LABEL`
    
    Examples
    --------
    
    Example 1 :
    
    data=pynsee.get_range_geo("DS_POPULATIONS_REFERENCE",lang="en")
    
    data.info()
    data.head()
    
    Example 2 :
    
    data=pynsee.get_range_geo("DS_TICM_PRATIQUES")
    
    data.info()
    data.head()
    
    """
    #Test pour savoir si la langue sélectionnée est fr ou en, si ce n'est pas le cas, on retourne un message d'erreur
    if lang not in ["fr","en"]:
        raise ValueError("lang must be 'fr' or 'en'")

    url = f"{base_url_melodi}/range/{ds_name}"

    try:
        #Requête pour récupérer les métadonnées avec les HEADERS et un timeout
        response = requests.get(url, timeout=30, headers=HEADERS)
        response.raise_for_status()
        response_data = response.json()

    #Gestion des erreurs réseau
    except requests.exceptions.HTTPError as e:
        status_code = (e.response.status_code if e.response is not None else "unknown")
        raise RuntimeError(
        f"HTTP Error {status_code}: The URL or resource might be incorrect:"
        f" {url}.")

    except requests.exceptions.Timeout:
        raise RuntimeError(
        "The request timed out. The server is taking too long to respond.")

    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
        f"The API did not return valid JSON for dataset '{ds_name}'.")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while requesting Mélodi API: {e}")

    data = pd.DataFrame(response_data.get("range", []))
    
    # Si data est vide
    if data.empty:
        raise ValueError(f"No range data found for dataset '{ds_name}'.")
    
    #Je découpe la variable concept en plusieurs colonnes
    info_concept = pd.json_normalize(data["concept"])
    data = data.drop(columns="concept").join(info_concept)
    
    #Je sélectionne uniquement la ligne GEO
    data=data.query('code=="GEO"').reset_index(drop=True)

    #Test pour savoir si la variable GEO est présente dans les concepts, si ce n'est pas le cas, on retourne un message d'erreur
    if data.shape[0] == 0:
        raise ValueError("No geographic information in the dataset")
    
    #Je récupère la liste des géographies
    liste_geo=pd.DataFrame(data["values"][0])
    liste_geo=liste_geo[["code","label","type","id"]]
    liste_geo["GEO_REF"] = liste_geo["id"].str.split("-").str[0]
    del liste_geo["id"] 

    #Je récupère les informations pour créer les colonnes liées à la variable GEO
    info_label = pd.json_normalize(liste_geo["label"])
    liste_geo = liste_geo.drop(columns="label").join(info_label)
    liste_geo =liste_geo.rename(columns={"code":"GEO","fr":"GEO_LABEL_FR","en":"GEO_LABEL_EN"})

    #Je récupère les informations pour créer les colonnes liées à la variable GEO_OBJECT
    info_type = pd.json_normalize(liste_geo["type"])
    liste_geo = liste_geo.drop(columns="type").join(info_type)
    liste_geo =liste_geo.rename(columns={"code":"GEO_OBJECT","fr":"GEO_OBJECT_LABEL_FR","en":"GEO_OBJECT_LABEL_EN"})

    #Je sélectionne les colonnes en fonction de la langue choisie
    if lang =="fr":
        liste_geo = liste_geo[["GEO_REF","GEO_OBJECT","GEO_OBJECT_LABEL_FR","GEO","GEO_LABEL_FR"]]
        liste_geo =liste_geo.rename(columns={"GEO_OBJECT_LABEL_FR":"GEO_OBJECT_LABEL","GEO_LABEL_FR":"GEO_LABEL"})
        
    elif lang =="en":
        liste_geo = liste_geo[["GEO_REF","GEO_OBJECT","GEO_OBJECT_LABEL_EN","GEO","GEO_LABEL_FR"]]
        liste_geo =liste_geo.rename(columns={"GEO_OBJECT_LABEL_EN":"GEO_OBJECT_LABEL","GEO_LABEL_FR":"GEO_LABEL"})
     
    #Trier liste_geo par GEO_OBJECT et GEO
    liste_geo = liste_geo.sort_values(by=["GEO_OBJECT","GEO"]).reset_index(drop=True)
    
    #Retourner le dataframe list_geo
    return liste_geo

# %%
