# -*- coding: utf-8 -*-

def _download_idbank_list():
    
    import requests
    import zipfile
    import tempfile
    import pandas as pd
    import os
    import re
    
    from ._hash import _hash
    from ._create_insee_folder import _create_insee_folder 
    from datetime import datetime

    file_to_dwn_default = "https://www.insee.fr/en/statistiques/fichier/2868055/2020_correspondance_idbank_dimension.zip"
    idbank_file_csv_default = "2020_correspondances_idbank_dimension.csv"
    
    insee_folder = _create_insee_folder()
    file = insee_folder + "/" + _hash(file_to_dwn_default) 

    trigger_update = False

    # if the data is not saved locally, or if it is too old (>90 days)
    # then an update is triggered

    if not os.path.exists(file): 
        trigger_update = True
    else: 
        try:
            # only used for testing purposes
            insee_date_time_now = os.environ['insee_date_test']
            insee_date_time_now = datetime.strptime(insee_date_time_now, '%Y-%m-%d %H:%M:%S.%f')
        except:
            insee_date_time_now = datetime.now()
         
        # file date creation
        file_date_last_modif =  datetime.fromtimestamp(os.path.getmtime(file))
        day_lapse = (insee_date_time_now - file_date_last_modif).days
        
        if day_lapse > 90:
            trigger_update = True   

    if trigger_update: 
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
            proxies = {'http': os.environ['http_proxy'],
                       'https': os.environ['https_proxy']}
        except:
            proxies = {'http': '', 'https': ''}
        
        try:
            results = requests.get(file_to_dwn, proxies = proxies)
            
            # create temporary directory
            dirpath = tempfile.mkdtemp()
            
            idbank_zip_file = dirpath + '\\idbank_list.zip'
            
            with open(idbank_zip_file, 'wb') as f:
                f.write(results.content)
            
            with zipfile.ZipFile(idbank_zip_file, 'r') as zip_ref:
                zip_ref.extractall(dirpath)

            if os.path.exists(idbank_zip_file):
                os.remove(idbank_zip_file)
        except:
            raise ValueError("!!! Idbank zip file not found !!!\nPlease change the value of  os.environ['insee_idbank_file_to_dwn']")
        
        file_to_read = [f for f in os.listdir(dirpath) if not re.match('.*.zip$', f)]
        
        if idbank_file_csv == file_to_read[0]:
            data = pd.read_csv(dirpath + "/" + file_to_read[0], dtype = 'str')    
            data.to_pickle(file)    
        else:
            raise ValueError("!!! Idbank file missing after unzipping \nPlease change the value of os.environ['insee_idbank_file_csv']!!!")
    else:        
        # pickle format depends on python version
        # then read_pickle can fail, if so
        # the file is removed and the function is launched again
        try:
            data = pd.read_pickle(file)  
        except:
            os.remove(file)
            data = _download_idbank_list()

    return data
    