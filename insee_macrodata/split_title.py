# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 16:29:34 2021

@author: XLAPDO
"""

def split_title(df, title_col_name = ["TITLE_EN", "TITLE_FR"],
                pattern = " – | — | - ", n_split = -1):
    
    import pandas as pd
            
    if isinstance(df, pd.DataFrame):        
        for title in title_col_name :
            if title in df.columns:
                try : 
                    df_title_splitted = df[title].str.split(pattern, n_split).tolist()
                except:
                    df_title_splitted = df[title].str.split(pattern).tolist()
                    
                df_title_splitted = pd.DataFrame(df_title_splitted, index = df.index)
                max_col = max(df_title_splitted.columns) + 1
                
                df_title_splitted.columns = [title + str(num + 1) for num in range(max_col)]
                
                df = pd.concat([df, df_title_splitted], axis = 1)
            else:
                print("!!! %s is not a column of the dataframe !!!" % title)
    else:
        print("!!! df is not a dataframe !!!")
    
    return(df)
