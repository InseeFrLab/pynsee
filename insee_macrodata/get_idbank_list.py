# -*- coding: utf-8 -*-
def get_idbank_list(*datasets, update = False):
    """Download an INSEE's series key list for one or several datasets
    Notes: Some metadata is stored for 3 months locally on the computer. It is updated automatically.
    Args:        
        update (bool, optional): Set to True, to update manually the metadata stored
         locally on the computer. Defaults to False.

    Raises:
        ValueError: datasets should be among the datasets list provided by get_dataset_list()

    Returns:
        DataFrame: contains dimension columns, series keys, dataset name 
    """    
    import pandas as pd
    import re
    
    from .get_dataset_list import get_dataset_list 
    from ._get_dataset_metadata import _get_dataset_metadata
    
    insee_dataset = get_dataset_list()    
    insee_dataset_list = insee_dataset['id'].to_list()
    
    for dt in datasets:
        if not dt in insee_dataset_list:               
            raise ValueError("%s is not a dataset from INSEE" % dt)
                
    idbank_list_dataset = []
    
    for dt in datasets:
        idbank_list_dt = _get_dataset_metadata(dt, update = update)
        
        idbank_list_dataset.append(idbank_list_dt)
            
    idbank_list = pd.concat(idbank_list_dataset)
    
    # label columns at the end
    
    r = re.compile(".*_label_.*")
    column_all = idbank_list.columns.to_list()
    column_label = list(filter(r.match, column_all))    
    column_other = [col for col in column_all if col not in column_label]    
    new_column_order = column_other + column_label
    
    idbank_list = pd.DataFrame(idbank_list, columns = new_column_order)
        
    return idbank_list