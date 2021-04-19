# -*- coding: utf-8 -*-
from functools import lru_cache

@lru_cache(maxsize=None)
def _warning_activity():
 msg1 = "!!! This function uses the latest data available (which is NAF/NACE rev. 2 - 2008), it may evolve over time !!!"
 print(msg1)

@lru_cache(maxsize=None)
def get_activity(level, version='latest'):
    """Get a list of economic activities from NAF/NACE rev 2 2008 classification

    Args:
        level (str): Levels available are : ['A10', 'A21', 'A38', 'A64', 'A88', 'A129', 'A138',
                       'NAF1', 'NAF2', 'NAF3', 'NAF4', 'NAF5']
        version (str, optional): Defaults to 'latest'. 

    Raises:
        ValueError: an error is raised if level is not in the default list
    """        
    import os, re
    import zipfile
    import pkg_resources
    import pandas as pd    
    
    from pynsee.utils._create_insee_folder import _create_insee_folder
    from pynsee.utils._paste import _paste
    from pynsee.metadata._get_naf import _get_naf
    from pynsee.metadata._get_nomenclature_agreg import _get_nomenclature_agreg
    
    level = level.upper()
    
    level_available = ['A10', 'A21', 'A38', 'A64', 'A88', 'A129', 'A138',
                       'NAF1', 'NAF2', 'NAF3', 'NAF4', 'NAF5']
    
    if not level in level_available:
        raise ValueError("!!! level must be in %s !!!", _paste(level_available, collapse = " "))
    
    _warning_activity()

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
                           'niv_agreg_naf_rev_2.csv', 
                           'table_NAF2-NA.csv']
                           
    list_expected_files = [insee_folder + '/naf2008/' + f for f in list_expected_files]
    
    list_available_file = [not os.path.exists(f) for f in list_expected_files]
    
    #unzipping raw files
    if any(list_available_file):
    
        zip_file = pkg_resources.resource_stream(__name__, 'data/naf.zip')
          
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(insee_folder)         
    
    
    def drop_space(string):
       if pd.isna(string):
           return(string)
       re_searched = re.search(' .*', string)
       if re_searched:
           string_found_cleaned = string.replace(" ", "")
       else:
           string_found_cleaned = string
       return(string_found_cleaned)
   
    if level in ['NAF5', 'NAF4', 'NAF3', 'NAF2', 'NAF1']:
         #read files
        naf_level = pd.read_csv(list_expected_files[1],
                                sep=";", encoding='latin', dtype=str)
        naf_level.columns = ['NAF5', 'NAF4', 'NAF3', 'NAF2', 'NAF1']
        
        naf = _get_naf(file=list_expected_files[0])
      
        naf = naf.rename(columns={"CODE": level,
                                  "TITLE_FR": "TITLE_" + level + "_FR",
                                  "TITLE_65CH_FR": "TITLE_" + level + "_65CH_FR",
                                  "TITLE_40CH_FR": "TITLE_" + level + "_40CH_FR"})       
        
        mapp = pd.read_csv(list_expected_files[10],
                           sep=";", encoding='latin', dtype=str)
        
        mapp = mapp.iloc[:,[0]+list(range(2,10))]
        mapp = mapp[mapp.index!=0]
        # mapp.columns = ['A732', 'A615', 'A272',
        #                 'A129', 'A88', 'A64', 'A38', 'A21', 'A10']
      
        mapp.columns = ['NAF5', 'NAF4', 'NAF3',
                        'A129', 'A88', 'A64', 'A38', 'A21', 'A10']
        mapp['NAF2'] =  mapp['A88']
        mapp['NAF1'] =  mapp['A21']
        
        mapp = mapp[[level, 'A129', 'A88', 'A64', 'A38', 'A21', 'A10']]        
                
        if level == 'NAF1':
            naf = naf[naf['len_code']==1]
            mapp = mapp[[level, 'A21', 'A10']]    
        if level == 'NAF2':
            naf = naf[naf['len_code']==2]        
            naf_level = naf_level[['NAF1', 'NAF2']]  
            mapp = mapp[[level, 'A88', 'A64', 'A38', 'A21', 'A10']]
        if level == 'NAF3':
            naf = naf[naf['len_code']==4]
            naf_level = naf_level[['NAF1', 'NAF2', 'NAF3']]
        if level == 'NAF4':
            naf = naf[naf['len_code']==5]
            naf_level = naf_level[['NAF1', 'NAF2', 'NAF3', 'NAF4']]
        if level == 'NAF5':
            naf = naf[naf['len_code']==6]
        
        if not level == 'NAF1':
            naf_level = naf_level.drop_duplicates()
            naf = naf.merge(naf_level, on=level, how="left")
        
        mapp = mapp.drop_duplicates()
        naf = naf.drop(columns=['len_code'])
        naf = naf.merge(mapp, on=level, how='left')
                
        return(naf)
    
    #
    df = _get_nomenclature_agreg(file=list_expected_files[9])
    
    icol = df.columns.get_loc(level)
    
    if level == 'A10':
        df = df[df["A10"] == df["A138"]]
    else:            
        level_before = df.columns[icol-1]
        df = df[df[level] != df[level_before]]
    
    df = df.drop_duplicates(subset = level, keep='first')
    
    if not level in ['A138', 'A129', 'A88']:
        level_after = df.columns[icol+1]
        df = df[df[level] == df[level_after]]
        
    seq = list(range(0, icol+1)) + [7]
    df = df.iloc[:,seq]
        
    df = df.rename(columns={'TITLE':'TITLE_' + level + '_FR'})
    df[level] = df[level].apply(drop_space)
                   
    if level == 'A138':
        ifile = 8
        ncol = 6
        first_col = 1
        label_list_col = ['A129', 'A138', 'NAF', 'TITLE_A138_EN', 'TITLE_A138_FR'] 
        col_merged = ['A138', 'TITLE_A138_EN']
        
    if level == 'A129':
        ifile = 8
        ncol = 6
        first_col = 1
        label_list_col = ['A129', 'A138', 'NAF', 'TITLE_A129_EN', 'TITLE_A129_FR'] 
        col_merged = ['A129', 'TITLE_A129_EN']
        
    if level == 'A88':
        ifile = 7
        ncol = 5
        first_col = 1
        label_list_col = ['', 'A88', 'TITLE_A88_EN', 'TITLE_A88_FR'] 
        col_merged = ['A88', 'TITLE_A88_EN']
    
    if level == 'A64':
        ifile = 6
        ncol = 4
        first_col = 0
        label_list_col = ['A64', 'NAF', 'TITLE_A64_EN', 'TITLE_A64_FR'] 
        col_merged = ['A64', 'TITLE_A64_EN']
    
    if level == 'A38':
        ifile = 5
        ncol = 4
        first_col = 0
        label_list_col = ['A38', 'NAF', 'TITLE_A38_EN', 'TITLE_A38_FR'] 
        col_merged = ['A38', 'TITLE_A38_EN']
    
    if level == 'A21':
        ifile = 4
        ncol = 4
        first_col = 1
        label_list_col = ['A21', 'TITLE_A21_EN', 'TITLE_A21_FR'] 
        col_merged = ['A21', 'TITLE_A21_EN']
    
    if level == 'A10':
        ifile = 2
        ncol = 5
        first_col = 0
        label_list_col = ['', 'A10', '' ,'TITLE_A10_EN', 'TITLE_A10_FR'] 
        col_merged = ['A10', 'TITLE_A10_EN']
        
    label = pd.read_csv(list_expected_files[ifile], sep=";", encoding='latin1', dtype=str)
    label = label.iloc[:,first_col:ncol]
    label.columns = label_list_col
    label = label.dropna(how='all')        
   
    label[level] = label[level].apply(drop_space)
    
    df = df.merge(label[col_merged], on = level, how = 'left')
    
    return(df)
        