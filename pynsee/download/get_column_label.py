
import pandas as pd

from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.utils._move_col_after import _move_col_before

def get_column_label(id):
    """
        Examples:
        >>> labels = get_colum_label("RP_INDREG_2016")
    
    """
    
    dict_data_source = _get_dict_data_source()  
    
    if id in dict_data_source.keys():
        
        dict_data = dict_data_source[id] 
        
        if "label_col" in dict_data.keys():
            labels = pd.DataFrame(dict_data["label_col"], index=[0]).T
            labels["column"] = labels.index
            labels.columns = ["label", "column"]
            labels = _move_col_before(labels, "column", "label")            
            labels = labels.reset_index(drop=True)
        else:
            print("Columns labels not found in metadata")
            labels = None            
    else:
        raise ValueError("id not found in file list, please check metadata from get_file_list")
    
    return labels
