# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd
from tqdm import trange

def _make_dataframe(data_request, main_key, query_number):
   
    list_dataframe = []    
        
    try:        
        data = data_request[main_key]          
    except:
        main_key_list = [key for key in list(data_request.keys()) if key != "header"]
        main_key = main_key_list[0]
        data = data_request[main_key]

    for i in trange(len(data), desc='{} - Getting data'.format(query_number)):
        idata = data[i]
        
        key_list = [key for key in idata.keys() if type(idata[key]) is list]
        key_not_list = [key for key in idata.keys() if type(idata[key]) is not list]
        
        key_dict = [key for key in idata.keys() if type(idata[key]) is dict]
        key_not_list_dict = [key for key in key_not_list if type(idata[key]) is not dict]
                    
        data_from_list = []        
        for key in key_list:
            df = pd.DataFrame(idata[key])
            data_from_list.append(df)
        
        newdict = { key : idata[key] for key in key_not_list_dict }
        
        data_other0 = pd.DataFrame(newdict, index=[0])
        
        data_from_dict = []
        for key in key_dict:
            df = pd.DataFrame(idata[key], index=[0])
            data_from_dict.append(df)
            
        if len(data_from_list) !=0:
            data_from_list = pd.concat(data_from_list).reset_index(drop=True)
            
            list_data_other = []
            for i in range(len(data_from_list.index)):
                list_data_other.append(data_other0)
            data_other = pd.concat(list_data_other).reset_index(drop=True)
            
            if len(data_from_dict) !=0:
                data_dict0 = pd.concat(data_from_dict, axis=1)
                list_data_dict = []
                for i in range(len(data_from_list.index)):
                    list_data_dict.append(data_dict0)      
                data_dict = pd.concat(list_data_dict).reset_index(drop=True)
                data_final = pd.concat([data_other, data_dict, data_from_list], axis=1)
            else:
                data_final = pd.concat([data_other, data_from_list], axis=1)

        else:
            if len(data_from_dict) !=0:
                data_dict0 = pd.concat(data_from_dict, axis=1)
                data_final =  pd.concat([data_other0, data_dict0], axis=1)
            else:
                data_final = data_other0   
                 
        
        list_dataframe.append(data_final)
        
    data_final = pd.concat(list_dataframe)
    
    return(data_final)