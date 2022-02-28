
from datetime import date
import tempfile
import os
import requests
import zipfile
import re
import pandas as pd



def _dwn_idbank_files():

    # creating the date object of today's date
    todays_date = date.today()

    main_link = "https://www.insee.fr/en/statistiques/fichier/2868055/"
        
    curr_year = todays_date.year
    last_year = curr_year - 1
    years = [str(curr_year), str(last_year)]

    months = [str(x) for x in range(12, 9, -1)]  + ["0" + str(x) for x in range(9, 0, -1)] 

    patt = "_correspondance_idbank_dimension"
    patterns = [y + x + patt for y in years for x in months]
    files = [main_link + f + ".zip" for f in patterns]

    try:
        file_to_dwn = os.environ["pynsee_idbank_file"]
    except:
        file_to_dwn = "https://www.insee.fr/en/statistiques/fichier/2868055/202201_correspondance_idbank_dimension.zip"

    try:
        data = _dwn_idbank_file(file_to_dwn = file_to_dwn)
    except:
        idbank_file_not_found = True
    else:
        idbank_file_not_found = False
    
    i = 0

    pynsee_idbank_loop_url = True

    try:
        pynsee_idbank_loop_url = os.environ["pynsee_idbank_loop_url"] 
        if (pynsee_idbank_loop_url == 'False') or (pynsee_idbank_loop_url == 'FALSE'):
            pynsee_idbank_loop_url = False       
    except:
        try:
            pynsee_idbank_loop_url = os.environ["PYNSEE_IDBANK_LOOP_URL"]   
            if (pynsee_idbank_loop_url == 'False') or (pynsee_idbank_loop_url == 'FALSE'):
                pynsee_idbank_loop_url = False    
        except:
            pass

    if pynsee_idbank_loop_url:
        while (idbank_file_not_found & (i<=len(files)-1)):        
            try:
                data = _dwn_idbank_file(file_to_dwn = files[i])
            except:
                idbank_file_not_found = True
            else:
                idbank_file_not_found = False
            i += 1

    return data



def _dwn_idbank_file(file_to_dwn):
    
    separator = ";"

    try:
        proxies = {'http': os.environ['http_proxy'],
                'https': os.environ['https_proxy']}
    except:
        proxies = {'http': '', 'https': ''}

    results = requests.get(file_to_dwn, proxies=proxies)

    dirpath = tempfile.mkdtemp()

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    idbank_zip_file = dirpath + '\\idbank_list.zip'

    with open(idbank_zip_file, 'wb') as f:
        f.write(results.content)
        f.close()

    with zipfile.ZipFile(idbank_zip_file, 'r') as zip_ref:
        zip_ref.extractall(dirpath)

    file_to_read = [f for f in os.listdir(dirpath) if not re.match('.*.zip$', f)]
    file2load = dirpath + "/" + file_to_read[0]
    data = pd.read_csv(file2load, dtype='str', sep=separator)

    return data
