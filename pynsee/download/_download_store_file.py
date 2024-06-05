import hashlib
import warnings
import difflib
import os
import tempfile

from pynsee.download._download_pb import _download_pb
from pynsee.download._import_options import _import_options
from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.download._check_url import _check_url

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
        suggestions = difflib.get_close_matches(id, dict_data_source.keys())

        if len(suggestions) == 0:
            error_message = (
                "No file id found. Check metadata from get_file_list function"
            )
        else:
            error_message = f"Data name might be mispelled, \
                potential values are: {suggestions}"

        raise ValueError(error_message)
        
    filename = os.path.join(tempfile.mkdtemp(), "tempfile")
    
    url_found = _check_url(caract["lien"])

    _download_pb(url=url_found, fname=filename, total=caract["size"])

    # CHECKSUM MD5 ------------------------------------------

    if hashlib.md5(open(filename, "rb").read()).hexdigest() != caract["md5"]:
        warnings.warn("File in insee.fr modified or corrupted during download")

    # PREPARE PANDAS IMPORT ARGUMENTS -----------------------

    pandas_read_options = _import_options(caract, filename)

    return {"result": caract, **pandas_read_options}
