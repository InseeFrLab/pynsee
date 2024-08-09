import io
import zipfile
import pkg_resources
import json


def _get_file_list_internal():

    zip_file = pkg_resources.resource_stream(
        __name__, "data/liste_donnees.zip"
    )

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_file = io.BytesIO(zip_ref.read("liste_donnees.json"))

    data = json.load(zip_file)

    return data
