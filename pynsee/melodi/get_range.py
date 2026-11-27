# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests
import pandas as pd

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% construction de la fonction get_range
def get_range(ds_name: str,
    base_url_melodi: str = "https://api.insee.fr/melodi",
    lang: str = "fr",
    exclusions_list: list = ["GEO"])-> pd.DataFrame:
    
    """
    
    Description
    ----------
    Get dataset range (codes and labels).
    Retrieves the list of dimensions and all their possible modalities values (codes and human-readable labels) for a given dataset.
    For GEO dimension, it is recommanded to used dedicated function : get_range_geo().
    
    Parameters
    ----------
    
    ds_name : dataset name
    
    base_url_melodi : API Melodi URL - default prod
    
    lang : french (fr) or english (en) labels - default french ("fr")
    
    exclusions_list : exclude some dimensions for a faster and light result - default : "GEO"
    
    Returns
    -------
    
    DataFrame with dimensions and modalities codes and labels
    
    Examples
    --------
    
    Example 1 :
    
    data=pynsee.get_range("DS_POPULATIONS_REFERENCE")
    
    data.info()
    data.head()
    
    Example 2 :
    
    data=pynsee.get_range(ds_name = "DS_EC_DECES",lang="en")
    
    data.info()
    data.head()
    """
    
    #Test pour savoir si la langue sélectionnée est fr ou en, si ce n'est pas le cas, on retourne un message d'erreur
    if lang not in ["fr","en"]:
        raise ValueError("lang must be 'fr' or 'en'")

    url=f"{base_url_melodi}/range/{ds_name}"

    try:
    #Requête pour récupérer les métadonnées
        response = requests.get(url, timeout=30,headers=HEADERS)
        response.raise_for_status()
        response_data = response.json()

    #Gestion des erreurs réseau
    except requests.exceptions.HTTPError as e:
        status_code = (e.response.status_code if e.response is not None else "unknown")
        raise RuntimeError(
        f"HTTP Error {status_code}: The URL or resource might be incorrect:"
        f" {url}.")

    #API trop longue
    except requests.exceptions.Timeout:
        raise RuntimeError(
        "The request timed out. The server is taking too long to respond.")

    #Json non valide
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
        f"The API did not return valid JSON for dataset '{ds_name}'.")

    #Autres erreurs
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while requesting Mélodi API: {e}")

    data = pd.DataFrame(response_data.get("range", []))

    #Si data est vide
    if data.empty:
        raise ValueError(f"No range data found for dataset '{ds_name}'.")

    #Récupérer les concepts (dimensions du dataset)
    concept=data.loc[:,"concept"]
    
    #Liste des codes et des libellés de concepts
    liste_code_concepts=[]
    liste_label_concepts_fr=[]
    liste_label_concepts_en=[]

    for item in concept:
        liste_code_concepts.append(item.get("code"))
        liste_label_concepts_fr.append(item.get("label", {}).get("fr"))
        liste_label_concepts_en.append(item.get("label", {}).get("en"))

    #Dataframe avec DIM et DIM_LABEL
    DIM_DIM_LABEL=pd.DataFrame({"DIM" : liste_code_concepts,
                     "DIM_LABEL_FR" : liste_label_concepts_fr,
                     "DIM_LABEL_EN" : liste_label_concepts_en})
    
    #Liste des modalités des variables
    values=data.loc[:,"values"]
    
    # Création d'une liste vide pour stocker les DataFrames de chaque dimension
    list_range_list = []
    
    # Parcours de chaque liste de modalités associée à une dimension
    for i, modalites_list in enumerate(values):
        # Si la liste de modalités est vide, on passe à la suivante
        if not modalites_list:
            continue
            
        mod_codes = []
        mod_labels_fr = []
        mod_labels_en = []
        
        for mod in modalites_list:
            mod_codes.append(mod.get("code"))
            lbl = mod.get("label", {})
            if isinstance(lbl, dict):
                mod_labels_fr.append(lbl.get("fr"))
                mod_labels_en.append(lbl.get("en"))
            else:
                mod_labels_fr.append(str(lbl))
                mod_labels_en.append(str(lbl))
                
        modalite = pd.DataFrame({
            "MOD": mod_codes,
            "MOD_LABEL_FR": mod_labels_fr,
            "MOD_LABEL_EN": mod_labels_en
        }).dropna(subset=["MOD"]) 
        
        # Ajout des informations sur les dimensions et leurs libellés (récupérées via l'index i)
        modalite["DIM"] = DIM_DIM_LABEL.loc[i, "DIM"]
        modalite["DIM_LABEL_FR"] = DIM_DIM_LABEL.loc[i, "DIM_LABEL_FR"]
        modalite["DIM_LABEL_EN"] = DIM_DIM_LABEL.loc[i, "DIM_LABEL_EN"]
        
        # Ajout du DataFrame de la dimension dans la liste globale
        list_range_list.append(modalite)
        
    # Concaténation de tous les sous-DataFrames en un seul grand DataFrame unifié
    if list_range_list:
        list_range = pd.concat(list_range_list, ignore_index=True)
    else:
        raise ValueError(f"No modalities found in range data for dataset '{ds_name}'.")
        
    #Je sélectionne les colonnes en fonction de la langue choisie
    if lang=="fr":
        list_range = list_range[["DIM","DIM_LABEL_FR","MOD","MOD_LABEL_FR"]]
        list_range =list_range.rename(columns={"DIM_LABEL_FR":"DIM_LABEL","MOD_LABEL_FR":"MOD_LABEL"})
        
    elif lang=="en":
        list_range = list_range[["DIM","DIM_LABEL_EN","MOD","MOD_LABEL_EN"]]
        list_range =list_range.rename(columns={"DIM_LABEL_EN":"DIM_LABEL","MOD_LABEL_EN":"MOD_LABEL"})
    
    #Enlever les dimensions à exclure, par défaut, on retire la GEO
    list_range=list_range[~list_range["DIM"].isin(exclusions_list)].reset_index(drop=True)
    
    #Trier list_range par DIM et MOD
    list_range = list_range.sort_values(by=["DIM","MOD"]).reset_index(drop=True)
    
    #Retourner le dataframe list_range
    return list_range

# %%
