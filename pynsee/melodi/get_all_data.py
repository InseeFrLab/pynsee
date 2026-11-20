# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import requests
import pandas as pd
import tempfile # Pour accéder au répertoire temporaire du système
import os
from tqdm import tqdm
import zipfile

# %% import des modules internes
from pynsee.melodi.get_metadata import get_metadata # import des fonctions internes du module nécessaire pour la fonction get_all_data

# %% import des modules internes
from pynsee.melodi.constants import HEADERS

# %% construction de la fonction get_all_data qui permet de télécharger à la fois le jeu de données et les métadatas
def get_all_data(ds_name: str,
                 base_url_melodi: str = "https://api.insee.fr/melodi",
                 download_directory: str = None,
                 stringsAsCategories: bool =False,
                 remove_file: bool = True):
       
    """
    
    Description
    ----------
    
    Get all data from a dataset.
    
    Parameters
    ----------
    
    ds_name : dataset name - use get_ds_list to find a dataset identifier
    
    base_url_melodi : API Melodi URL - default production URL : "https://api.insee.fr/melodi"
    
    download_directory : download directory - default system tempdir
    
    stringsAsCategories : if TRUE, strings variables in DataFrame are converted to categories - default FALSE
    
    remove_file : remove downloaded data file after loading data - default TRUE
    
    Returns
    -------
    
    A tuple consisting of one DataFrame holding the data and another holding the metadata.
    
    Examples
    --------
    
    tuple=pynsee.get_all_data("DS_TICM_PRATIQUES")

    #data
    data=tuple[0]
    data.info()
    data.head()
    
    #metadata
    metadata=tuple[1]
    metadata.info()
    metadata.head()
    """
    
    #Si aucun répertoire de téléchargement n'est précisé, utiliser le dossier temporaire par défaut
    if download_directory is None:
        download_directory = tempfile.gettempdir()
            
    ds_products=get_metadata(ds_name, base_url_melodi)["product"]

    csv_list = [fichier for fichier in ds_products if fichier["format"]=="CSV"]
        
    #Si aucun fichier csv pour le DS => erreur
    if len(csv_list) == 0:
        raise ValueError(f"Error : no CSV found for {ds_name}")
            
    #Si plusieurs fichiers CSV pour le DS => erreur
    elif len(csv_list) > 1:
        raise ValueError(f"Error : more than 1 CSV found for {ds_name}")
        
    zip_url=csv_list[0]["accessURL"]
    print(f"Request ZIP CSV file : {zip_url}")

    #Déterminer le chemin local où le fichier sera sauvegardé
    downloaded_zip_path = os.path.join(download_directory,f"{ds_name}.zip")

    #Téléchargenement du zip + bar de progression dnas la console
    with requests.get(zip_url, stream=True,timeout=30, headers=HEADERS) as r: # requête api avec un alias à r
        r.raise_for_status()# si erreur requête => on arrête le traitement
        total = int(r.headers.get('content-length', 0)) # on cherche à récupérer la taille total du fichier si possible (pour la barre de progression), si non dispo => 0 
        with open(downloaded_zip_path, 'wb') as f,tqdm(# ouvre un fichier pour y stocker le contenu de la requête
            total=total, unit='B', unit_scale=True, desc="Downloading the file"# tqdm permet de faire une barre de progression de téléchargement
        ) as pbar:
            # boucle qui permet d'enregister d'écrire dans le zip morceau par morceau
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk:
                    f.write(chunk) # écriture par morceau
                    pbar.update(len(chunk)) # met à jour la barre de progression
                    
    #Ouvre l'archive ZIP
    with zipfile.ZipFile(downloaded_zip_path, 'r') as archive: #permet d'ouvrir une archive zip
        #Liste tous les fichiers contenus
        print("Listing of files :", archive.namelist())
        
        #Chercher le fichier qui se termine par "_data.csv" dans la liste des fichiers de l'archive
        file_list=archive.namelist()
        csv_data= next((name for name in file_list if name.endswith("_data.csv")),
                  None)
        if csv_data is None:
            raise FileNotFoundError("No file with '_data.csv' at the end")
        with archive.open(csv_data) as file_data: #permet d'ouvrir un fichier dans une archive zip
            data = pd.read_csv(filepath_or_buffer=file_data,sep=";",decimal=".",dtype={"GEO": "string"},low_memory=False)#importer le fichier csv en DataFrame
        
        #Chercher le fichier qui se termine par "_metadata.csv" dans la liste des fichiers de l'archive
        csv_metadata= next((name for name in file_list if name.endswith("_metadata.csv")),
                  None)
        if csv_metadata is None:
            raise FileNotFoundError("No file with '_metadata.csv' at the end")
        with archive.open(csv_metadata) as file_metadata: # permet d'ouvrir un fichier dans une archive zip
            metadata = pd.read_csv(filepath_or_buffer=file_metadata,sep=";",decimal=".")# importer le fichier csv en DataFrame

    #Permet de supprimer l'archive une fois les dataframes chargés
    if remove_file:
        if os.path.exists(downloaded_zip_path):
            os.remove(downloaded_zip_path)
            print("Remove downloaded files.")
        else:
            print("File not found.")

    #Permet transformer les types de variables object/string en category
    if stringsAsCategories:
        print("Before type conversion :")
        data.info()
        for col in data.select_dtypes(include=["object", "string"]).columns:
            data[col] = data[col].astype("category")
        print("After type conversion :")
        data.info()
    
    return data, metadata
