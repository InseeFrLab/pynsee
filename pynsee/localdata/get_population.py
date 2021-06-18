# -*- coding: utf-8 -*-

from functools import lru_cache
import os
import zipfile
import pkg_resources
import pandas as pd

from pynsee.utils._create_insee_folder import _create_insee_folder    

@lru_cache(maxsize=None)
def _warning_pop_data():
    print("!!! This function renders only package's internal data, it might not be the most up-to-date\nHave a look at insee.fr !!!")


@lru_cache(maxsize=None)
def get_population():    
    """Get population data on all French communes (cities) 

    Notes:
        Source : Insee, demographic census.
        Geographic codes are from the 2020 classification.

        Have a look at : https://www.insee.fr/fr/statistiques/3698339#consulter

    Examples:
        >>> from pynsee.localdata import get_population
        >>> pop = get_population()
    """    
    insee_folder = _create_insee_folder()

    insee_folder_pop = insee_folder + '/' + 'pop'
    
    if not os.path.exists(insee_folder_pop):
        os.mkdir(insee_folder_pop)  
    
    list_files = os.listdir(insee_folder_pop)
    
    list_wanted_files = ['base-pop-historiques-1876-2018.csv', 'var.csv']    
        
    test_available_file = [not f in list_files for f in list_wanted_files]
    
    if any(test_available_file):
    
        zip_file = pkg_resources.resource_stream(__name__, 'data/pop.zip')
            
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(insee_folder)  
            
    df = pd.read_csv(insee_folder_pop + '/' + 'base-pop-historiques-1876-2018.csv', dtype=str)
    label = pd.read_csv(insee_folder_pop + '/' + 'var.csv', dtype=str)
    
    # clean data and rename columns
    df = df.iloc[4:,:]
    df.columns = df.iloc[0,:]
    df = df.iloc[1:,:]
    
    list_id_vars = ['CODGEO', 'REG', 'DEP', 'LIBGEO']
    list_value_vars = [f for f in df.columns if f not in list_id_vars]
    
    df = df.melt(id_vars = list_id_vars, value_vars = list_value_vars,
                 var_name='VARIABLE', value_name='OBS_VALUE')
    
    label = label.iloc[4:,:]
    label.columns = label.iloc[0,:]
    label = label.iloc[4:,:]
    label.columns = ['VARIABLE', 'YEAR', 'VARIABLE_TITLE_FR']
    
    def extract_year(string):
        str_cleaned = string.replace('Population en ', '')
        return(str_cleaned)
    
    label['YEAR'] = label['YEAR'].apply(extract_year)
    
    df = df.merge(label, on = 'VARIABLE', how = 'left')
    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')    
    
    _warning_pop_data()
    
    return(df)
