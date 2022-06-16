from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.utils._move_col_after import _move_col_before
import pandas as pd

def _get_value_label(id):
    
    dict_data_source = _get_dict_data_source()  
    val_col = None
    
    if id in dict_data_source.keys():
        
        dict_data = dict_data_source[id] 
        
        if "val_col" in dict_data.keys():
            val_col = dict_data["val_col"]  
            
    return val_col


def _add_metadata(id, df):
    
    val_col = _get_value_label(id)
    
    if val_col is not None:
        
        for k in val_col.keys():
            val_col_df = pd.DataFrame(val_col[k], index=[0]).T
            val_col_df[k] = val_col_df.index
            val_col_df.columns = [k + "_label_fr", k]
            val_col_df[k] = val_col_df[k].astype(str)
            
            if k in df.columns:
                df = df.merge(val_col_df, on = k, how = "left")
                
                if df[k + "_label_fr"].isnull().values.all():
                    del df[k + "_label_fr"]
    else:
        print("No column-specific metadata has been found for this file")
    
    return df