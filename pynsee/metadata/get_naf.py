# -*- coding: utf-8 -*-

def get_naf(level):
        
    import os, re
    import zipfile
    import pkg_resources
    import pandas as pd    
    
    from pynsee.utils._create_insee_folder import _create_insee_folder
    from pynsee.utils._paste import _paste
    
    level_available = ['A10', 'A21', 'A38', 'A64', 'A88', 'A129', 'A138', 'NAF']
    
    if not level in level_available:
        raise ValueError("!!! level must be in %s !!!", _paste(level_available, collapse = " "))
    
    insee_folder = _create_insee_folder()

    insee_folder_local_naf = insee_folder + '/' + 'naf'
    
    if not os.path.exists(insee_folder_local_naf):
        os.mkdir(insee_folder_local_naf)  
    
    list_expected_files = ['int_courts_naf_rev_2.csv',
                           'naf2008_5_niveaux.csv',
                           'int_eng_na_2008_a10.csv',
                           'int_eng_na_2008_a17.csv',
                           'int_eng_na_2008_a21.csv',
                           'int_eng_na_2008_a38.csv',
                           'int_eng_na_2008_a64.csv',
                           'int_eng_na_2008_a88.csv',
                           'int_eng_na_2008_a138.csv',
                           'niv_agreg_naf_rev_2.csv']
                           
    list_expected_files = [insee_folder + '/naf2008/' + f for f in list_expected_files]
    
    list_available_file = [not os.path.exists(f) for f in list_expected_files]
    
    #unzipping raw files
    if any(list_available_file):
    
        zip_file = pkg_resources.resource_stream(__name__, 'data/naf.zip')
          
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(insee_folder)         
    
    #read files
    data = pd.read_csv(list_expected_files[0], sep=";", encoding='latin1')
    #level = pd.read_csv(list_expected_files[1], sep=";", encoding='latin')
    
    #data cleaning    
    data = data.iloc[:,1:5]
    data.columns = ['CODE', 'TITLE_FR', 'TITLE_65CH_FR', 'TITLE_40CH_FR']
    data = data.dropna()
    
    def clean_CODE_col(string):
        re_searched = re.search('^SECTION .*$', string)
        if re_searched:
            string_found = re_searched.group(0)
            string_found_cleaned = string_found.replace("SECTION ", "")
        else:
            string_found_cleaned = string
        return(string_found_cleaned)
    
    data['CODE'] = data['CODE'].apply(clean_CODE_col)
    
    #
    df = pd.read_csv(list_expected_files[9], sep=";", encoding='latin1', dtype=str)
    
    for i in range(len(df.index)):
        for j in range(2,len(df.columns)):
            if pd.isna(df.iloc[i,j]):
                df.iloc[i,j] = df.iloc[i,j-1]
    
    for j in range(len(df.columns)):
        for i in range(len(df.index)):        
            if pd.isna(df.iloc[i,j]):
                df.iloc[i,j] = df.iloc[i-1,j]
                
    df = df.iloc[:,1:10]
    df.columns = ['A10', 'A21', 'A38', 'A64', 'A88', 'A129', 'A138', 'TITLE']
    
    def get_nom(nom=level, data=df):
        icol = data.columns.get_loc(nom)
        if nom == 'A10':
            data = data[data["A10"] == data["A138"]]
        else:            
            nom_before = data.columns[icol-1]
            data = data[data[nom] != data[nom_before]]
        
        data = data.drop_duplicates(subset = level, keep='first')
        
        if not nom in ['A138', 'A129', 'A88']:
            nom_after = data.columns[icol+1]
            data = data[data[nom] == data[nom_after]]
            
        seq = list(range(0, icol+1)) + [7]
        data_final = data.iloc[:,seq]
        return(data_final)
    
    data_final = get_nom()
    
    if 'A88' in data_final.columns:
        A88_loc = data_final.columns.get_loc("A88")
        data_final.insert(A88_loc+1, 'A88_bis', data_final['A21'] +  data_final['A88'])
        data_final = data_final.replace({'A88_bis': {"LILI": "LI"}})
    
    data_final = data_final.rename(columns={'TITLE':'TITLE_' + level})
    
    return(data_final)
        