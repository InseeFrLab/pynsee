import zipfile
import pkg_resources
import json

from pynsee.utils._create_insee_folder import _create_insee_folder


def _get_file_list_internal():

    zip_file = pkg_resources.resource_stream(__name__, "data/liste_donnees.zip")

    insee_folder = _create_insee_folder()
    data_file = insee_folder + "/" + "liste_donnees.json"

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(insee_folder)

    with open(data_file, "r") as f:
        data = json.load(f)

    return data
