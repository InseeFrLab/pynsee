from pynsee.download._get_dict_data_source import _get_dict_data_source


def _get_value_label(id):

    dict_data_source = _get_dict_data_source()
    val_col = None

    if id in dict_data_source.keys():

        dict_data = dict_data_source[id]

        if "val_col" in dict_data.keys():
            val_col = dict_data["val_col"]

    return val_col


"""
def _add_metadata(id, df):
    
    val_col = _get_value_label(id)
    
    if val_col is not None:
        
        list_df_metadata = []
        
        for kindex in trange(len(val_col.keys()), desc= "Adding Metadata"):
            k = list(val_col.keys())[kindex]
            val_col_df = pd.DataFrame(val_col[k], index=[0]).T
            val_col_df[k] = val_col_df.index
            val_col_df.columns = [k + "_label_fr", k]
            val_col_df[k] = val_col_df[k].astype(str)
            
            if k in df.columns:
                dfk = df[[k]].merge(val_col_df, on = k, how = "left")
                
                if not dfk[k + "_label_fr"].isnull().values.all():
                    list_df_metadata += [dfk[[k + "_label_fr"]]]
        
        if len(list_df_metadata) > 0:
            df = pd.concat([df] + list_df_metadata, axis=1)
        
    else:
        print("No column-specific metadata has been found for this file")
    
    return df
"""
