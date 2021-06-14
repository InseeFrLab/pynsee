# -*- coding: utf-8 -*-

from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata.get_series_list import get_series_list
from pynsee.macrodata.search_macrodata import search_macrodata
from tqdm import trange
import os
import pandas as pd

def _build_series_list(dt=["CNA-2014-ERE"]):
        
    #
    # SET dt = None TO BUILD THE FULL DATA FRAME
    #
    
    os.environ['pynsee_use_sdmx'] = "True"
    
    if dt is None:
        dt = get_dataset_list()
        dt = dt.id.to_list()
        
    list_dt = []
    
    for d in trange(len(dt)):
        dataset = dt[d]
        df = get_series_list(dataset, update=True)
        list_dt.append(df)
        
    series_list = pd.concat(list_dt)    
    # series_list.to_csv("pynsee_series_all.csv")
    
    os.environ['pynsee_use_sdmx'] = "False"
    
    old_series = search_macrodata()
    old_series = old_series.drop(columns = {"KEY"})
    series_list_short = series_list[["DATASET", "IDBANK", "KEY"]]
    
    series_list_new = series_list_short.merge(old_series, on = ["DATASET", "IDBANK"], how = "left")
    
    series_list_new_title_missing = series_list_new[pd.isna(series_list_new['TITLE_FR'])]
    series_list_new_title_missing = series_list_new_title_missing.drop(columns = {"TITLE_FR", "TITLE_EN"})
    
    list_series_title_missing = series_list_new_title_missing.IDBANK.to_list()
    
    if len(list_series_title_missing) > 0:
        pass
    
    return(series_list)

#IPPMP
#IPPMP-NF
#ENQ-CONJ-IND-BAT
#IPC-2015
#IPC-PM-2015
#IPPI-2015
#IPPS-2015
#IRL
#IPCH-2015
#NAISSANCES-FECONDITE
#MARIAGE-NUPTIALITE
#POPULATION-STRUCTURE
    
    
    
    