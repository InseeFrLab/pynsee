# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

# %% import des modules externes
import pandas as pd

# %% import des modules internes
from pynsee.melodi.get_data import get_data
from pynsee.melodi.constants import HEADERS

# %% construction de la fonction get_local_data_by_com qui permet d'interroger l'API melodi via URL et d'avoir les indicateurs au niveau communale pour un territoire englobant à choisir
def get_local_data_by_com(ds_name: str,
                          geo: str,
                          geo_object: str,
                          query_filter: str ="",
                          base_url_melodi: str ="https://api.insee.fr/melodi") -> pd.DataFrame:
       
    """
    
    Description
    ----------
    
    Get data on every Commune of one territory.
    
    Parameters
    ----------
    
    ds_name : dataset name - use get_ds_list to find a dataset identifier
    
    geo : code geo
    
    geo_object : geo level
    
    query_filter : additionnal filter on request - default : ""
    
    base_url_melodi : API Melodi URL - default production URL : "https://api.insee.fr/melodi"

    Returns
    -------
    
    DataFrame with data.
    
    Examples
    --------
    
    Example 1 :
    
    data=pynsee.get_local_data_by_com(
        
      ds_name = "DS_POPULATIONS_REFERENCE",
      
      geo = "69",
      
      geo_object = "DEP")

    data.info()
    data.head()
    
    Example 2 :
    
    data=pynsee.get_local_data_by_com(
        
      ds_name = "DS_POPULATIONS_REFERENCE",
      
      geo = "69",
      
      geo_object = "DEP",
      
      query_filter = "POPREF_MEASURE=PMUN")
        
    data.info()
    data.head()
    """
    
    if query_filter != "":
        query_filter=f"&{query_filter}"
        
    url=f"{base_url_melodi}/data/{ds_name}?GEO={geo_object}-{geo}*COM{query_filter}"
    
    return get_data(url)
