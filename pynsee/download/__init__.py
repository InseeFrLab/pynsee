# import difflib
# import hashlib
# import os
# import re
# import tempfile
# import warnings
# import zipfile
# from pathlib import Path
# from shutil import copyfileobj, move

# import pandas as pd
# import requests
# import tqdm.auto as tqdma
# from tqdm import tqdm
# from tqdm.utils import CallbackIOWrapper

from pynsee.download.load_data import load_data
from pynsee.download.get_file_list import get_file_list

__all__ = ["load_data", "get_file_list"]

# READ ALL DATA SOURCES AVAILABLE USING JSON ONLINE FILE ----------------




# data = "FILOSOFI_AU2010"
# date = "dernier"
# teldir = None
# load_data("RP_LOGEMENT", date = "2016")
# load_data("FILOSOFI_AU2010", "dernier")



# deprecated names ----------------

"""

def telechargerFichier(data, date=None, teldir=None):
    warnings.warn('
        WARNING: \n
        telechargerFichier was an experimental name and might be deprecated in the future\n
        Please use the new function name 'download_store_file' instead
    ', DeprecationWarning)
    return download_store_file(data=data, date=date, teldir=teldir)


def chargerDonnees(telechargementFichier: dict, variables=None):
    warnings.warn('
        WARNING: \n
        chargerDonnees was an experimental name and might be deprecated in the future\n
        Please use the new function name 'load_data_from_schema' instead
    ', DeprecationWarning)
    insee_data = load_data_from_schema(
        telechargementFichier=telechargementFichier,
        variables=variables)
    return insee_data


def telechargerDonnees(data, date, teldir=None,
                       variables_names=None
                       ):
    warnings.warn('
        WARNING: \n
        telechargerDonnees was an experimental name and might be deprecated in the future\n
        Please use the new function name 'load_data' instead
    ', DeprecationWarning)
    insee_data = load_data(
        data=data,
        date=date,
        teldir=teldir,
        variables_names=variables_names)
    return insee_data


def millesimesDisponibles(data):
    warnings.warn('
        WARNING: \n
        millesimesDisponibles was an experimental name and might be deprecated in the future\n
        Please use the new function name 'check_year_available' instead
    ', DeprecationWarning)
    return check_year_available(data=data)


"""