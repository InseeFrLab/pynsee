
import pandas as pd

from pynsee.download._get_value_label import _get_value_label
from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.utils._move_col_after import _move_col_before

def get_column_metadata(id):
    """ Get metadata about an insee.fr file
    
    Returns:
        Returns the request dataframe as a pandas object
            
    Examples:
        >>> from pynsee.download import get_column_metadata
        >>> rp_logement_metadata = get_column_metadata("RP_LOGEMENT_2016")
        
    """ 
    
    dict_data_source = _get_dict_data_source()  
    
    if id in dict_data_source.keys():
        
        dict_data = dict_data_source[id] 
        
        if "label_col" in dict_data.keys():
            labels = pd.DataFrame(dict_data["label_col"], index=[0]).T
            labels["column"] = labels.index
            labels.columns = ["column_label_fr", "column"]
            labels = _move_col_before(labels, "column", "column_label_fr")            
            labels = labels.reset_index(drop=True)
        else:
            print("Columns labels not found in metadata")
            labels = None
        
        val_col = _get_value_label(id)

        if val_col is not None:
            
            list_val_col = []

            for k in val_col.keys():
                val_col_df = pd.DataFrame(val_col[k], index=[0]).T
                val_col_df[k] = val_col_df.index
                val_col_df.columns = ["value" + "_label_fr", "value"]
                val_col_df["value"] = val_col_df["value"].astype(str)
                val_col_df["column"] = k
                list_val_col += [val_col_df]
            
            if len(list_val_col) > 0:
                concat_list = pd.concat(list_val_col).reset_index(drop=True)
                labels = labels.merge(concat_list, on = ["column"], how = "left")
                labels = labels[["column", "value", "value_label_fr", "column_label_fr"]]
                print("Column-specific metadata has been found for this file")
                    
    else:
        raise ValueError("id not found in file list, please check metadata from get_file_list")
    
    return labels
