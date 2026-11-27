# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests
import pandas as pd
import json

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% création de la fonction get_catalog qui permet de lister les jeux de données accessibles dans melodi

def get_catalog(lang: str = "fr",
                base_url_melodi: str = "https://api.insee.fr/melodi") -> pd.DataFrame:

    """

    Description
    ----------
    
    Get list of available datasets.

    Parameters
    ----------
    
    lang : str, {"fr", "en"}, default "fr"
        Language of metadata.
        
    base_url_melodi : str, default "https://api.insee.fr/melodi"
        Base URL of the Melodi API.

    Returns
    -------
    
    DataFrame with columns: identifier, title_content,
    subtitle_content, description_content, abstract_content,
    temporal_startPeriod, temporal_endPeriod, modified,
    numObservations, numSeries.

    Raises
    ------
    
    ValueError
        If ``lang`` is not 'fr' or 'en'.

    Examples
    --------
    Example 1: Get the catalog in French (default)

    catalogue_melodi = pynsee.get_catalog()
    catalogue_melodi.head()

    Example 2: Get the catalog in English
    
    catalogue_melodi = pynsee.get_catalog(lang="en")
    catalogue_melodi.head()
    """

    # Test pour savoir si la langue sélectionnée est fr ou en, si ce n'est pas, 
    # on retourne un message d'erreur
    if lang not in ("fr", "en"):
        raise ValueError("lang must be 'fr' or 'en'")

    # Requête qui permet d'accéder à la liste des datasets du catalogue Mélodi
    requete_dataset = base_url_melodi + "/catalog/all"
    print(f"Catalog request : {requete_dataset}")
    
    try:
        response = requests.get(url=requete_dataset, stream=True, timeout=30,headers=HEADERS)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
        data = response.json()

    #Gestion des erreurs réseau
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        raise RuntimeError(f"HTTP Error {status_code}: The URL or resource might be incorrect: {requete_dataset}.")

    #API trop longue
    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. The server is taking too long to respond.")
    
    #Autres erreurs
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while requesting Mélodi API: {e}")

    # Transformer en DataFrame
    data = pd.DataFrame(data)

    # Fonction d'extraction dynamique basée sur le code langue
    def extract_content(x, target_lang):
        if isinstance(x, list):
            for item in x:
                if isinstance(item, dict) and item.get("lang") == target_lang:
                    return item.get("content")
        return None

    # Dans la boucle, on récupère les titres, sous-titres, descriptions et les résumés
    for col in ("title", "subtitle", "description", "abstract"):
        data[f"{col}_content"] = data[col].apply(extract_content,
                                                 target_lang=lang)

    # récupérer le début de période des DS
    data["temporal_startPeriod"] = data["temporal"].apply(
        lambda x: x.get("startPeriod") if isinstance(x, dict) else None)

    # récupérer la fin de période des DS
    data["temporal_endPeriod"] = data["temporal"].apply(
        lambda x: x.get("endPeriod") if isinstance(x, dict) else None)

    # Sélection des variables
    all_dataset_extract = data.loc[:, ["identifier", "title_content",
                                       "subtitle_content", "description_content",
                                       "abstract_content", "temporal_startPeriod",
                                       "temporal_endPeriod", "modified",
                                       "numObservations", "numSeries"]]

    # Retourne le DataFrame all_dataset_extract
    return all_dataset_extract

# %%
