# -*- coding: utf-8 -*-

def split_title(df, title_col_name = ["TITLE_EN", "TITLE_FR"],
                pattern = " – | — | - ", n_split = -1):
    """Split the title columns

    Args:
        df DataFrame: a DataFrame created by get_insee_idbank or get_insee_dataset
        title_col_name (list, optional): Names of the title columns. Defaults to ["TITLE_EN", "TITLE_FR"].
        pattern (str, optional): Separator string. Defaults to " – | — | - ".
        n_split (int, optional): Number of split, 1 corresponds to 2 columns. Defaults to -1, i.e. the maximun.
    
    Examples:  
        >>> from pynsee.macro import *   
        >>> data_raw = get_insee_idbank("001577236")
        >>> data = split_title(data_raw)
    """    
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
