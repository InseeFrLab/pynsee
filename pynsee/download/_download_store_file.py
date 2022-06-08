import requests
import hashlib
import warnings
from pathlib import Path
from tqdm import tqdm

from pynsee.download._info_data import _info_data
from pynsee.download._download_pb import _download_pb
from pynsee.download._import_options import _import_options
from pynsee.download._initialize_temp_directory import _initialize_temp_directory

def _download_store_file(data: str, date=None, teldir=None):
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

    caract = _info_data(data, date)
    cache = False

    if teldir is None:
        cache = True
        temporary_file, teldir = _initialize_temp_directory()
    else:
        Path(teldir).mkdir(parents=True, exist_ok=True)

    filename = temporary_file.name

    # DOWNLOAD FILE ------------------------------------------

    out_request = requests.get(caract['lien'], stream=True)
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

    if cache:
        print(f"\
            No destination directory defined.\n  \
            Data have been written there: {filename}"
            )
    else:
        print(
            f"File has been written there : {filename}"
            )

    # CHECKSUM MD5 ------------------------------------------

    if hashlib.md5(open(filename, 'rb').read()).hexdigest() != caract['md5']:
        warnings.warn("File in insee.fr modified or corrupted during download")

    # PREPARE PANDAS IMPORT ARGUMENTS -----------------------

    pandas_read_options = _import_options(caract, filename)

    return {"result": caract, **pandas_read_options}