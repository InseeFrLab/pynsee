# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests
import tempfile # Pour accéder au répertoire temporaire du système
import os

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% création de la fonction get_file qui permet de télécharger soit un fichier excel associé à un DS soit le csv melodi complet, soit le DS complet au format parquet

def get_file(ds_name: str,
              download_file_name: str = None,
              file_name: str = None,
              download_directory: str = None,
              base_url_melodi: str = "https://api.insee.fr/melodi") -> str:

    """
  
    Description
    ----------   
    
    Get file attached to a dataset : extract (XLSX), or full CSV file, or full parquet file.

    Parameters
    ----------
    
    ds_name : dataset name
    
    file_name : file name, optional. Omit this parameter to get the Parquet file
    
    download_file_name : filename on disk after download, optional. Omit this parameter to get the Parquet file
    
    download_directory : download directory - default system tempdir
    
    base_url_melodi : API Melodi URL - default production URL : "https://api.insee.fr/melodi"
    
    Returns
    -------
    
    The path of the downloaded file.
    
    Examples
    --------
    
    Example 1 : download the XLSX associated with a dataset
        
    pynsee.get_file(ds_name = "DS_EC_DECES",
             file_name = "T1_DECES_JOUR_NAT_FR",
             download_file_name = "T1_DECES_JOUR_NAT_FR.xlsx")
    
    Example 2 : download the CSV in an archive that corresponds to the dataset
    
    pynsee.get_file(ds_name = "DS_EC_DECES",
             file_name = "DS_EC_DECES_CSV_FR",
             download_file_name = "DS_EC_DECES_CSV_FR.zip")

    Example 3 : download the parquet file that corresponds to the dataset
        
    pynsee.get_file(ds_name = "DS_RP_SERIE_HISTORIQUE")
    """

    #Si un file_name est fourni, download_file_name est obligatoire
    if file_name is not None and download_file_name is None:
        raise ValueError("download_file_name must be specified when file_name is provided.")
    
    #Si aucun répertoire de téléchargement n'est précisé, utiliser le dossier temporaire par défaut
    if download_directory is None:
        download_directory = tempfile.gettempdir()

    if file_name is None:
        #Construire l'URL complète pour télécharger le parquet
        url = f"{base_url_melodi}/file/{ds_name}/PARQUET"
        download_file_name = ds_name + ".parquet"
    else :
        #Construire l'URL complète à partir des paramètres pour télécharger xlsx ou csv
        url = f"{base_url_melodi}/file/{ds_name}/{file_name}"

    #Déterminer le chemin local où le fichier sera sauvegardé
    path = os.path.join(download_directory, download_file_name)

    #Afficher l'URL demandée
    print(f"Request file : {url}")

    #Afficher le chemin local du fichier téléchargé
    print(f"Downloaded path : {path}")

    try:   
        #Envoyer une requête GET à l'URL (avec téléchargement en flux pour les gros fichiers)
        response = requests.get(url, stream=True, timeout=(30, 120),headers=HEADERS)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes

        #Ouvrir le fichier local en mode écriture binaire et écrire les données par blocs
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):  # Lire le contenu par morceaux
                if chunk:  # Éviter d’écrire des blocs vides
                    f.write(chunk)
    #Gestion des erreurs réseau
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        raise RuntimeError(f"HTTP Error {status_code}: The URL or resource might be incorrect: {url}.")

    #API trop longue
    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. The server took too long to respond or the download stalled.")

    #Autres erreurs
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error while requesting Mélodi API: {e}")


    #Retourner le chemin du fichier téléchargé
    return path


# %%
