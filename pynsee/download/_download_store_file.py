import requests
import hashlib
import warnings
from pathlib import Path
from tqdm import tqdm
import difflib
import os

from pynsee.download._info_data import _info_data
from pynsee.download._download_pb import _download_pb
from pynsee.download._import_options import _import_options
from pynsee.download._get_dict_data_source import _get_dict_data_source

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
from pynsee.utils._warning_cached_data import _warning_cached_data

def _download_store_file(id: str, update: bool):
    """Download requested file and return some metadata that will
    be used

    Arguments:
        data {str} -- The name of the dataset desired

    Keyword Arguments:
        date -- Optional argument to specify desired year (default: {None})
        teldir -- Desired location where data
            should be stored (default: {None})

    Raises:
        ValueError: When the desired dataset
        is not found on insee.fr,
        an error is raised

    Returns:
        dict -- If everything works well, returns a dictionary
    """
    
    dict_data_source = _get_dict_data_source()
    if id in dict_data_source.keys():
        caract = dict_data_source[id]
    else:   
        suggestions = difflib.get_close_matches(
            id,
            dict_data_source.keys()
            )
        
        if len(suggestions) == 0:
            error_message = "No file id found. Check metadata from get_file_list function"
        else:
            error_message = f"Data name might be mispelled, \
                potential values are: {suggestions}"
            
        raise ValueError(error_message)  
    
    insee_folder = _create_insee_folder()
    filename = insee_folder + \
            "/" + _hash("pynsee.download" + id)          
    
    if (not os.path.exists(filename)) or update:
        
        try:
            proxies = {'http': os.environ['http_proxy'],
                    'https': os.environ['https_proxy']}
        except:
            proxies = {'http': '', 'https': ''}
        
        out_request = requests.get(caract['lien'], proxies=proxies, stream=True)
        
        if out_request.status_code == 200:
            _download_pb(url=caract['lien'], fname=filename, total=caract['size'])
        else:
            raise ValueError(
                """
                File not found on insee.fr.
                Please open an issue on
                https://github.com/InseeFrLab/Py-Insee-Data to help
                improving the package
                """)
    else:
        _warning_cached_data(filename)
    
    # CHECKSUM MD5 ------------------------------------------

    if hashlib.md5(open(filename, 'rb').read()).hexdigest() != caract['md5']:
        warnings.warn("File in insee.fr modified or corrupted during download")

    # PREPARE PANDAS IMPORT ARGUMENTS -----------------------

    pandas_read_options = _import_options(caract, filename)

    return {"result": caract, **pandas_read_options}