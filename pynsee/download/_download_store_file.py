import difflib
import hashlib
import logging
import os
import re
import tempfile
import warnings

from pynsee.download._download_pb import _download_pb
from pynsee.download._import_options import _import_options
from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.download._check_url import _check_url


logger = logging.getLogger(__name__)


def _download_store_file(tempdir: tempfile.TemporaryDirectory, id: str):
    """Download requested file and return some metadata that will
    be used

    Arguments:
        tempdir {tempfile.TemporaryDirectory} -- The temporary folder where the dataset should be written
        id {str} -- The name of the dataset desired

    Raises:
        ValueError: When the desired dataset
        is not found on insee.fr,
        an error is raised

    Returns:
        dict -- If everything works well, returns a dictionary
    """

    dict_data_source = _get_dict_data_source()
    caract = None
    if id in dict_data_source.keys():
        caract = dict_data_source[id]
    elif id.rsplit("_", 1)[-1].lower() == "latest":
        # allow to query a dataset with a custom "latest" TAG (for instance
        # "TAG_COM_..." only exists as a vintaged dataset) for stability
        # purposes
        root = id.rsplit("_", 1)[0]
        suggestions = {
            x
            for x in dict_data_source.keys()
            if re.match(root + ".?[0-9]{4}", x)
        }
        if suggestions:
            new_id = sorted(suggestions)[-1]
            logger.warning(
                "File %s not found. Switching to %s instead", id, new_id
            )
            caract = dict_data_source[new_id]

    if not caract:
        suggestions = difflib.get_close_matches(id, dict_data_source.keys())
        if len(suggestions) == 0:
            error_message = (
                "No file id found. Check metadata from get_file_list function"
            )
        else:
            error_message = f"Data name might be mispelled, \
                potential values are: {suggestions}"

        raise ValueError(error_message)

    filename = os.path.join(tempdir, "tempfile")

    url_found = _check_url(caract["lien"])

    _download_pb(url=url_found, fname=filename, total=caract["size"])

    # CHECKSUM MD5 ------------------------------------------

    with open(filename, "rb") as f:
        if hashlib.md5(f.read()).hexdigest() != caract["md5"]:
            warnings.warn(
                "File in insee.fr modified or corrupted during download"
            )

    # PREPARE PANDAS IMPORT ARGUMENTS -----------------------

    pandas_read_options = _import_options(tempdir, caract, filename)

    return {"result": caract, **pandas_read_options}
