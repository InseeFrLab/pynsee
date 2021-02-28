# -*- coding: utf-8 -*-

def _get_dataset_metadata(dataset, update=False):
    
    import pandas as pd
    import os
    
    from datetime import datetime    
        
    from ._download_idbank_list import _download_idbank_list
    from ._get_dataset_dimension import _get_dataset_dimension
    from ._get_dimension_values import _get_dimension_values
    from ._create_insee_folder import _create_insee_folder
    from ._get_idbank_internal_data import _get_idbank_internal_data
    from ._hash import _hash  
    
    try:        
        insee_folder = _create_insee_folder()
        file_dataset_metadata = insee_folder + "/" + _hash("idbank_list" + dataset)
        
        trigger_update = False
        
        if not os.path.exists(file_dataset_metadata): 
            trigger_update = True
            print("%s : metadata update triggered because a file is missing" % dataset)
        else:
           
            try:
                # only used for testing purposes
                insee_date_time_now = os.environ['insee_date_test']
                insee_date_time_now = datetime.strptime(insee_date_time_now, '%Y-%m-%d %H:%M:%S.%f')
            except:
                insee_date_time_now = datetime.now()
             
            # file date creation
            file_date_last_modif =  datetime.fromtimestamp(os.path.getmtime(file_dataset_metadata))
            day_lapse = (insee_date_time_now - file_date_last_modif).days
            
            if day_lapse > 90:
                trigger_update = True
                print("%s : metadata update triggered because the file is older than 3 months" % dataset)   
        
        if update: 
            trigger_update = True
            print("%s : metadata update triggered manually" % dataset)
        
        if trigger_update:        
        
            idbank_list = _download_idbank_list()
            
             # get dataset's dimensions
            dataset_dimension = _get_dataset_dimension(dataset)
            
            # select only the idbanks corresponding to the dataset
            idbank_list_dataset = idbank_list[idbank_list["nomflow"] == dataset]
            
            # split the cleflow column with the dot as a separator
            df_cleflow_splitted = idbank_list_dataset.cleFlow.str.split('\\.').tolist()
            
            # make a dataframe from the splitted cleflow
            new_columns = dataset_dimension.dimension.to_list()
            df_cleflow_splitted = pd.DataFrame(df_cleflow_splitted, columns = new_columns)
            
            # join the splitted cleflow dataframe with the former idbank list
            idbank_list_dataset = pd.concat([idbank_list_dataset.reset_index(drop = True),
                                             df_cleflow_splitted], axis = 1)      
                
            n_dimensions = len(dataset_dimension.index)
            
            for irow in range(n_dimensions):
                
                dim_id = dataset_dimension['dimension'].iloc[irow]
                dim_local_rep = dataset_dimension['local_representation'].iloc[irow]
                
                # get dimension values
                dim_values = _get_dimension_values(dim_local_rep)
                
                # drop dimension label
                dim_values = dim_values[dim_values["id"] != dim_local_rep]
                
                # rename columns
                dim_values.columns = [dim_id, dim_id + '_label_fr', dim_id + '_label_en']
                
                idbank_list_dataset = idbank_list_dataset.merge(dim_values,
                                                                on = dim_id, how = 'left')
            # save data
            idbank_list_dataset.to_pickle(file_dataset_metadata)
            
        else:
            # pickle format depends on python version
            # then read_pickle can fail, if so
            # the file is removed and the function is launched again
            try:
                idbank_list_dataset = pd.read_pickle(file_dataset_metadata) 
            except:
                os.remove(file_dataset_metadata)
                idbank_list_dataset = _get_dataset_metadata(dataset, update=update)               
                   
            # print("Cached data has been used")
    except:
        # if the download of the idbank file and the build of the metadata fail
        # package's internal data is provided to the user, should be exceptional, used as a backup
        print("!!! Warning: Package's internal data has been used !!!")
        idbank_list_dataset = _get_idbank_internal_data()
        idbank_list_dataset = idbank_list_dataset[idbank_list_dataset["nomflow"] == dataset]
        # drop the columns where all elements are NaN
        idbank_list_dataset = idbank_list_dataset.dropna(axis=1, how='all')
        
    return(idbank_list_dataset)
   