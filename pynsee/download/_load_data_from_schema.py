import os
from shutil import copyfileobj, move
import pandas as pd

from pynsee.download._unzip_pb import _unzip_pb

def _load_data_from_schema(
    telechargementFichier: dict,
    variables=None,
    limit_chunk_size=1000000000):
    """Using options derived from `download_store_file`, import dataset in python

    Arguments:
        telechargementFichier {dict} -- Options needed for import

    Keyword Arguments:
        variables {list} -- A subset of variables that should be used (default: {None})

    Raises:
        ValueError: If the file is not found, an error is raised

    Returns:
        pd.DataFrame -- The required dataset is returned as pd.DataFrame object
    """
    if telechargementFichier["result"]["zip"] is True:
        print(telechargementFichier['file_archive'])
        _unzip_pb(
            telechargementFichier['file_archive'],
            f"{telechargementFichier['import_args']['file']}_temp"
            )
        move(
            f"{telechargementFichier['import_args']['file']}_temp/{telechargementFichier['result']['fichier_donnees']}",
            telechargementFichier["import_args"]['file']
            )

    if os.path.isfile(telechargementFichier["file_to_import"]) is False:
        raise ValueError("File cannot be found")

    if telechargementFichier["result"]["type"] == "csv":
        if os.path.getsize(telechargementFichier["file_to_import"]) >= limit_chunk_size:
            chunk = pd.read_csv(telechargementFichier["file_to_import"], 
                                chunksize=1000000, 
                                dtype="str",
                                delimiter = telechargementFichier["import_args"]["delim"])
            df_insee = pd.concat(chunk)
        else:
            try:
                df_insee = pd.read_csv(
                    telechargementFichier["file_to_import"],
                    delimiter=telechargementFichier["import_args"]["delim"],
                    dtype="str",
                    usecols=variables
                    )
            except:
                encoding = telechargementFichier["import_args"]["encoding"]
                useEncoding = True
                if isinstance(encoding, str):
                    if encoding == "Nan":
                        useEncoding = False
                else:
                    useEncoding = False
                    
                if not useEncoding:
                    df_insee = pd.read_csv(
                        telechargementFichier["file_to_import"],
                        delimiter=telechargementFichier["import_args"]["delim"],
                        dtype="str",
                        usecols=variables,
                        engine="python"
                        )
                else:
                    
                    df_insee = pd.read_csv(
                        telechargementFichier["file_to_import"],
                        delimiter=telechargementFichier["import_args"]["delim"],
                        dtype="str",
                        usecols=variables,
                        engine="python",
                        encoding=encoding
                        )
                    
    elif telechargementFichier["result"]["type"] in ["xls", "xlsx"]:
        df_insee = pd.read_excel(
            telechargementFichier["file_to_import"],
            sheet_name=telechargementFichier["import_args"]["sheet"],
            skiprows=telechargementFichier["import_args"]["skip"],
            nrows=telechargementFichier["import_args"]["n_max"],
            na_values=telechargementFichier["import_args"]["na"],
            dtype="str",
            usecols=variables
            )
    elif telechargementFichier["result"]["type"] == "JSON":
        raise ValueError("Not yet implemented")

    return df_insee