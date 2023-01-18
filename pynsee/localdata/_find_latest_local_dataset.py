
import sys
import os
import re
from tqdm import trange
import datetime
import pickle

from pynsee.localdata._get_insee_local_onegeo import _get_insee_local_onegeo
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def _find_latest_local_dataset(dataset_version, variables, update):
    
    filename = _hash("".join([dataset_version] + ['_find_latest_local_dataset']))
    insee_folder = _create_insee_folder()
    file_localdata = insee_folder + "/" + filename 
    
    if (not os.path.exists(file_localdata)) or update:
    
        datasetname = dataset_version.replace('latest', '').replace('GEO', '')

        current_year = int(datetime.datetime.today().strftime('%Y'))   
        backwardperiod = 5
        list_geo_dates = range(current_year, current_year-backwardperiod, -1)        
        list_data_dates = range(current_year, current_year-backwardperiod, -1)

        list_dataset_version = ['GEO' + str(gdate) + datasetname + str(ddate)
                        for gdate in list_geo_dates
                        for ddate in list_data_dates]

        for dvindex in trange(len(list_dataset_version),
                              desc='Finding Latest Dataset Version'):

            dv = list_dataset_version[dvindex]

            try:
                sys.stdout = open(os.devnull, 'w')
                df = _get_insee_local_onegeo(
                            variables, dv, nivgeo='FE', codegeo='1'
                        ) 
                sys.stdout = sys.__stdout__
            except:            
                if dv == list_dataset_version[-1]:
                    msg = '!!! Latest dataset version not found !!!\n'
                    msg += 'Please, consider having a look at api.insee.fr or get_local_metadata function'
                    raise ValueError(msg)
            else:
                dataset_version = dv
                break
            
        pickle.dump(dataset_version, open(file_localdata, "wb"))
    else:
        try:
            dataset_version = pickle.load(open(file_localdata, "rb"))
        except:
            os.remove(file_localdata)
            dataset_version = _find_latest_local_dataset(
                variables=variables,
                dataset_version=dataset_version,
                update=True
            )
        else:
            print("Latest dataset version previously found has been used\nSet update=True to get the most up-to-date data")
        
    return dataset_version