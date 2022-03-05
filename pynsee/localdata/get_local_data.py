# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
from functools import lru_cache
from tqdm import trange
import pandas as pd
import numpy as np

from pynsee.localdata._get_insee_local_onegeo import _get_insee_local_onegeo
from pynsee.localdata.get_geo_list import get_geo_list
from pynsee.localdata._warning_local_data import _warning_local_data

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

@lru_cache(maxsize=None)
def _warning_nivgeo(nivgeo):
    if nivgeo == "DEP":
        nivgeo_label = "departements"
        print(f"By default, the query is on all {nivgeo_label}")
    elif nivgeo == "REG":
        nivgeo_label = "regions"
        print(f"By default, the query is on all {nivgeo_label}")
    elif nivgeo == "FE":
        print("By default, the query is on all France territory")


def get_local_data(variables, dataset_version, nivgeo='FE', geocodes=['1'], update=False):
    """Get INSEE local numeric data

    Args:
        variables (str): one or several variables separated by an hyphen (see get_local_metadata)

        dataset_version (str): code of a dataset version (see get_local_metadata)

        nivgeo (str): code of kind of French administrative area (see get_nivgeo_list), by default it is 'FE' ie all France

        geocodes (list): code one specific area (see get_geo_list), by default it is ['1'] ie all France

        update (bool): data is saved locally, set update=True to trigger an update

    Raises:
        ValueError: Error if geocodes is not a list

    Examples:
        >>> from pynsee.localdata import get_local_metadata, get_nivgeo_list, get_geo_list, get_local_data
        >>> metadata = get_local_metadata()
        >>> nivgeo = get_nivgeo_list()
        >>> departement = get_geo_list('departements')
        >>> #
        >>> data_all_france = get_local_data(dataset_version='GEO2020RP2017',
        >>>                        variables =  'SEXE-DIPL_19')
        >>> #
        >>> data_91_92 = get_local_data(dataset_version='GEO2020RP2017',
        >>>                        variables =  'SEXE-DIPL_19',
        >>>                        nivgeo = 'DEP',
        >>>                        geocodes = ['91','92'])
    """

    if type(geocodes) != list:
        raise ValueError("!!! geocodes must be a list !!!")
    
    if (geocodes == ["1"]) or (geocodes == ["all"]) or (geocodes == "all"):
        if nivgeo == "DEP":            
            departement = get_geo_list('departements')
            geocodes = departement.CODE.to_list()
            _warning_nivgeo(nivgeo)          
        elif nivgeo == "REG":            
            reg = get_geo_list('regions')
            geocodes = reg.CODE.to_list()
            _warning_nivgeo(nivgeo)
        elif (nivgeo == "FE"):
            _warning_nivgeo(_warning_nivgeo) 
        elif (nivgeo != "METRODOM"):
            print("!!! Please, provide a list with geocodes argument !!!")            

    filename = _hash("".join([variables] + [dataset_version] + [nivgeo] + geocodes))
    insee_folder = _create_insee_folder()
    file_localdata = insee_folder + "/" + filename

    if (not os.path.exists(file_localdata)) or update:

        list_data_all = []

        for cdg in trange(len(geocodes), desc="Getting data"):

            codegeo = geocodes[cdg]
            try:
                df = _get_insee_local_onegeo(
                    variables, dataset_version, nivgeo, codegeo)
            except:
                df = pd.DataFrame({'CODEGEO': codegeo, 'OBS_VALUE': np.nan}, index=[0])

            list_data_all.append(df)

        data_final = pd.concat(list_data_all).reset_index(drop=True)
        data_final.to_pickle(file_localdata)
        print(f'Data saved: {file_localdata}')

    else:
        try:
            data_final = pd.read_pickle(file_localdata)
        except:
            os.remove(file_localdata)
            data_final = get_local_data(variables=variables, 
                                    dataset_version=dataset_version, nivgeo=nivgeo, 
                                    geocodes=geocodes, update=True)
        else:
            print(f'Locally saved data has been used\nSet update=True to trigger an update')

    _warning_local_data()

    return(data_final)
