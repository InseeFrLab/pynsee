# -*- coding: utf-8 -*-


def _clean_naf_row(df, col = 'NAF'):
    import re
    import pandas as pd
    
    list_add_row = []
    for i in range(len(df.index)):
        naf_string_comma = re.search(",", df.loc[i, col])
        
        if naf_string_comma:
            string_splitted = df.loc[i, col].split(",")
            data0 = df.drop(columns=[col]).iloc[[i]].reset_index(drop=True)
            data=data0
            for i in range(len(string_splitted)-1):
                data = pd.concat([data, data0])
            data = data.reset_index(drop=True)
            added_rows = pd.DataFrame({col:string_splitted})
            added_rows = pd.concat([added_rows, data],axis=1)
            list_add_row.append(added_rows)
        
        naf_string_accent = re.search(r'\u00E0', df.loc[i, col])
        if naf_string_accent:
            num_left_pattern = re.compile(r'^\d+')
            num_left = num_left_pattern.findall(df.loc[i, col])[0]
            
            num_right_pattern = re.compile(r'\d+.\d+')
            num_right = num_right_pattern.findall(df.loc[i, col])
            num_right = [string.replace(num_left, "").replace(".", "")  for string in num_right]
            num_range = list(range(int(num_right[0]), int(num_right[1])+1))
            
            naf_added = [num_left + '.' + str(num) for num in num_range]
            
            data0 = df.drop(columns=[col]).iloc[[i]].reset_index(drop=True)
            data=data0
            for i in range(len(naf_added)-1):
                data = pd.concat([data, data0])
            data = data.reset_index(drop=True)
            
            added_rows = pd.DataFrame({col:naf_added})
            added_rows = pd.concat([added_rows, data],axis=1)
            list_add_row.append(added_rows)
            
    added_rows_final = pd.concat(list_add_row)
     #match comma and a with accent
    rows_kept = [(re.search(",|" + r'\u00E0', df.loc[i, col]) is None) for i in range(len(df.index))]
    data_kept = df.loc[rows_kept,:]
     
    data_final = pd.concat([data_kept, added_rows_final]).reset_index(drop=True)
    return(data_final)