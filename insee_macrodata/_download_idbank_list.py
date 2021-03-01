# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def _download_idbank_list():
    
    import requests
    import zipfile
    import tempfile
    import pandas as pd
    import os
    import re
    
    file_to_dwn_default = "https://www.insee.fr/en/statistiques/fichier/2868055/2020_correspondance_idbank_dimension.zip"
    idbank_file_csv_default = "2020_correspondances_idbank_dimension.csv"
    
    try:
        file_to_dwn = os.environ['insee_idbank_file_to_dwn']
    except:
        file_to_dwn = file_to_dwn_default
    try:
        idbank_file_csv = os.environ['insee_idbank_file_csv']
    except:
        idbank_file_csv = idbank_file_csv_default

    #download file
    try:
        proxies = {'http': os.environ['http'],
                   'https': os.environ['https']}
    except:
        proxies = {'http': '','https': ''}
    
    try:
        results = requests.get(file_to_dwn, proxies = proxies)
        
        # create temporary directory
        dirpath = tempfile.mkdtemp()
        
        idbank_zip_file = dirpath + '\\idbank_list.zip'
        
        with open(idbank_zip_file, 'wb') as f:
            f.write(results.content)
        
        with zipfile.ZipFile(idbank_zip_file, 'r') as zip_ref:
            zip_ref.extractall(dirpath)
    except:
        ValueError("!!! Idbank zip file not found !!!\nPlease change the value of  os.environ['insee_idbank_file_to_dwn']")
    
    file_to_read = [f for f in os.listdir(dirpath) if not re.match('.*.zip$', f)]
    
    if idbank_file_csv == file_to_read[0]:
        data = pd.read_csv(dirpath + "/" + file_to_read[0], dtype = 'str')
        return data
    else:
        ValueError("!!! Idbank file missing after unzipping \nPlease change the value of os.environ['insee_idbank_file_csv']!!!")
    
    