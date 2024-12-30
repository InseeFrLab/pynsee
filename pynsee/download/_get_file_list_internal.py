import io
import zipfile
import importlib
import json


def _get_file_list_internal():

    zip_file = str(importlib.resources.files(__name__)) + "/data/liste_donnees.zip"

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_file = io.BytesIO(zip_ref.read("liste_donnees.json"))

    data = json.load(zip_file)

    return data
