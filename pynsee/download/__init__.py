import warnings
import hashlib
import tempfile
import os
import requests
import json
import re
import zipfile
from pathlib import Path
from Levenshtein import distance as lev
import pandas as pd
from shutil import move, copyfileobj

# import tqdm.auto as tqdma
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

# READ ALL DATA SOURCES AVAILABLE USING JSON ONLINE FILE -------------------------------

url_data_list = "https://raw.githubusercontent.com/InseeFrLab/DoReMIFaSol/master/data-raw/liste_donnees.json"
jsonfile = requests.get(url_data_list).json()

# HACK BECAUSE OF DUPLICATED ENTRIES -------------------------------

potential_keys = [items['nom'] for items in jsonfile]
list_duplicated_sources = list(set([x for x in potential_keys if potential_keys.count(x) > 1]))


def create_key(item, duplicate_sources):
    """
    Transform JSON into Python dict

    Args:
        item: Item in JSON source
        duplicate_sources: List of duplicate sources in JSON

    Returns: Initial dict with modified keys to avoid duplicated entries

    """
    if item['nom'] not in duplicate_sources:
        return item['nom']
    dateref = item["date_ref"]
    year = re.search(r'\d{4}', dateref).group(0)
    return '{}_{}'.format(item['nom'], year)


dict_data_source = {create_key(item, list_duplicated_sources): item for item in jsonfile}


# data = "FILOSOFI_AU2010"
# date = "dernier"
# teldir = None
# load_data("RP_LOGEMENT", date = "2016")
# load_data("FILOSOFI_AU2010", "dernier")

def load_data(data, date, teldir=None, #argsApi=None,
                       variables_names=None #,force=False
                       ):
    """
    User level function to download datasets from insee.fr

    Args:
        data: Dataset name
        date: Year. Can be an integer. Can also be 'recent' or 'latest' to get latest dataset
        teldir: Where output should be written
        variables_names: Subset of variable names to use. If None (default), ignored

    Returns:
        Returns the request dataframe as a pandas object

    """
    try:
        return load_data_from_schema(
            download_store_file(data=data, date=date, teldir=teldir),
            variables_names
        )
    except:
        raise ValueError("Download failed")


def download_pb(url: str, fname: str, total: int = None):
    """Useful function to get request with a progress bar

    Borrowed from https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51

    Arguments:
        url {str} -- URL for the source file
        fname {str} -- Destination where data will be written
    """
    resp = requests.get(url, stream=True)

    if total is None:
        total = int(resp.headers.get('content-length', 0))

    with open(fname, 'wb') as file, tqdm(
            desc='Downloading: ',
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def unzip_pb(fzip, dest, desc="Extracting"):
    """
    Useful function to unzip with progress bar
    Args:
        fzip: Filename of the zipped file
        dest: Destination where data must be written
        desc: Argument inherited from zipfile.ZipFile

    Returns:
        zipfile.Zipfile(fzip).extractall(dest) with progress
    """

    dest = Path(dest).expanduser()
    Path(dest).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(fzip) as zipf, tqdm(
            desc=desc, unit="B", unit_scale=True, unit_divisor=1024,
            total=sum(getattr(i, "file_size", 0) for i in zipf.infolist()),
    ) as pbar:
        for i in zipf.infolist():
            if not getattr(i, "file_size", 0):  # directory
                zipf.extract(i, os.fspath(dest))
            else:
                with zipf.open(i) as fi, open(os.fspath(dest / i.filename), "wb") as fo:
                    copyfileobj(CallbackIOWrapper(pbar.update, fi), fo)



def initialize_temp_directory():
        """A wrapper to initialize temporary directories

        Returns:
            Nothing, just creates the temporay directories
        """
    tf = tempfile.NamedTemporaryFile(delete=False)
    teldir = tempfile.TemporaryDirectory()
    Path(teldir.name).mkdir(parents=True, exist_ok=True)
    print("Data will be stored in the following location: {}".format(teldir.name))
    return tf, teldir


def download_store_file(data: str, date=None, teldir=None):
    """Download requested file and return some metadata that will
    be used

    Arguments:
        data {str} -- The name of the dataset desired

    Keyword Arguments:
        date -- Optional argument to specify desired year (default: {None})
        teldir -- Desired location where data should be stored (default: {None})

    Raises:
        ValueError: When the desired dataset
        is not found on insee.fr,
        an error is raised

    Returns:
        dict -- If everything works well, returns a dictionary
    """

    caract = info_donnees(data, date)
    cache = False

    if teldir is None:
        cache = True
        tf, teldir = initialize_temp_directory()
    else:
        Path(teldir).mkdir(parents=True, exist_ok=True)

    # IF DOES NOT USE API REST ------

    # filename = "{}/{}".format(teldir.name, os.path.basename(caract['lien']))
    filename = tf.name


    # DOWNLOAD FILE ------------------------------------------

    r = requests.get(caract['lien'], stream=True)
    if r.status_code == 200:
        download_pb(url=caract['lien'], fname=filename, total=caract['size'])
    else:
        raise ValueError(
            "File not found on insee.fr. Please open an issue on https://github.com/InseeFrLab/Py-Insee-Data to help improving the package")

    if cache:
        print("No destination directory defined. Data have been written there: {}".format(
            filename
        ))
    else:
        print("File has been written there : {}".format(
            filename
        ))

    # CHECKSUM MD5 ------------------------------------------

    if hashlib.md5(open(filename, 'rb').read()).hexdigest() != caract['md5']:
        warnings.warn("File in insee.fr modified or corrupted during download")


    # PREPARE PANDAS IMPORT ARGUMENTS -----------------------

    pandas_read_options = import_options(caract, filename)

    return {"result": caract, **pandas_read_options}



def import_options(caract: dict, filename: str):
    """ Internal to generate a dictionary of options
    required to import files

    Arguments:
        caract {dict} -- Dictionary returned by `download_store_file`
        filename {str} -- Filename of the object that is going to be imported

    Returns:
        dict -- A dictionary listing options to control
         import with `pandas`
    """

    if caract["zip"] is True:
        fileArchive = filename
        fichierAImporter = "{}/{}".format(tempfile.gettempdir(), caract['fichier_donnees'])
    else:
        fileArchive = None
        fichierAImporter = filename

    argsImport = {"file": fichierAImporter}

    if caract['type'] == "csv":
        argsImport.update({"delim": caract['separateur'], "col_names": True})
        if 'encoding' in list(caract.keys()):
            argsImport.update({"locale": caract["encoding"]})
    elif caract['type'] in ["xls", "xlsx"]:
        argsImport.update({'path': fichierAImporter, "skip": caract['premiere_ligne'] - 1})
        if 'onglet' in list(caract.keys()):
            argsImport.update({"sheet": caract["onglet"]})
        else:
            argsImport.update({"sheet": 0})
        if 'derniere_ligne' in list(caract.keys()):
            argsImport.update({"n_max": caract["derniere_ligne"] - caract["premiere_ligne"]})
        else:
            argsImport.update({"n_max": None})

        if 'valeurs_manquantes' in list(caract.keys()):
            argsImport.update({"na": caract["valeurs_manquantes"]})
        else:
            argsImport.update({"na": None})

    if 'type_col' in list(caract.keys()):
        list_cols = caract["type_col"]
        for key, value in list_cols.items():
            if value == "character":
                list_cols[key] = "str"
            elif value == "integer":
                list_cols[key] = "int"
            elif value == "number":
                list_cols[key] = "float"
    else:
        list_cols = None

    argsImport.update({"dtype": list_cols})

    return {'fileArchive': fileArchive, 'fichierAImporter': fichierAImporter,
            'argsImport': argsImport}


def load_data_from_schema(telechargementFichier: dict, vars=None):
    """Using options derived from `download_store_file`, import dataset in python

    Arguments:
        telechargementFichier {dict} -- Options needed for import

    Keyword Arguments:
        vars {list} -- A subset of variables that should be used (default: {None})

    Raises:
        ValueError: If the file is not found, an error is raised

    Returns:
        pd.DataFrame -- The required dataset is returned as pd.DataFrame object
    """
    if telechargementFichier["result"]["zip"] is True:
        unzip_pb(telechargementFichier['fileArchive'], "{}_temp".format(telechargementFichier["argsImport"]['file']))
        move("{}_temp/{}".format(telechargementFichier["argsImport"]['file'],
                                     telechargementFichier["result"]['fichier_donnees']),
                 telechargementFichier["argsImport"]['file'])

    if os.path.isfile(telechargementFichier["fichierAImporter"]) is False:
        raise ValueError("File cannot be found")

    if telechargementFichier["result"]["type"] == "csv":
        if os.path.getsize(telechargementFichier["fichierAImporter"])>=1000000000:
            chunk=pd.read_csv(telechargementFichier["fichierAImporter"],chunksize=1000000)
            df=pd.concat(chunk)
        else:
            df = pd.read_csv(telechargementFichier["fichierAImporter"],
                         delimiter=telechargementFichier["argsImport"]["delim"],
                         dtype=telechargementFichier["argsImport"]["dtype"],
                         usecols=vars
                         )
    elif telechargementFichier["result"]["type"] in ["xls", "xlsx"]:
        df = pd.read_excel(telechargementFichier["fichierAImporter"],
                           sheet_name=telechargementFichier["argsImport"]["sheet"],
                           skiprows=telechargementFichier["argsImport"]["skip"],
                           nrows=telechargementFichier["argsImport"]["n_max"],
                           na_values=telechargementFichier["argsImport"]["na"],
                           dtype=telechargementFichier["argsImport"]["dtype"],
                           usecols=vars
                           )
    elif telechargementFichier["result"]["type"] == "JSON":
        raise ValueError("Not yet implemented")

    return df


def info_donnees(data : str, date=None):
    """Get some info regarding datasets available

    Arguments:
        data {str} -- Dataset name

    Keyword Arguments:
        date -- Desired year for the dataset (default: {None})


    Returns:
        For instance, looks for closed match in the
         keyword given to download_store_file
    """

    if date == "latest":
        date = "dernier"

    donnees = data.upper()
    liste_nom = dict_data_source.keys()
    liste_nom_no_suffix = [re.sub(r'_\d{4}$', '', x) for x in liste_nom]
    res = [i for i, x in enumerate(liste_nom_no_suffix) if x == donnees]

    if not len(res):
        # looking for close match (Levenshtein distance)
        dist = dict(zip(liste_nom_no_suffix, [lev(donnees, l) for l in liste_nom_no_suffix]))
        suggestions = []
        for key, value in dist.items():
            if value < 6: suggestions += ['\"{}\"'.format(key)]
        if suggestions:
            error_message = "Data name is mispelled, potential values are: {}".format(", ".join(suggestions))
        else:
            error_message = "No data found. Did you mispelled ?"
        raise ValueError(error_message)

    # 2 - gestion millésimes

    possible = check_year_available(donnees)

    if (len(possible) > 1) & (date is None):
        raise ValueError("Several versions of this dataset exist, please specify a year")

    if date == "dernier":
        latest = sorted(possible.keys(), key=lambda x: x.lower(), reverse=True)[0]
        possible = possible[latest]
    elif date is not None:
        possible = possible["{}_{}".format(donnees, str(date))]

    return possible


def check_year_available(data):
    donnees = data.upper()
    liste_nom = dict_data_source.keys()
    liste_nom_no_suffix = [re.sub(r'_\d{4}$', '', x) for x in liste_nom]
    res = [i for i, x in enumerate(liste_nom_no_suffix) if x == donnees]

    if bool(res) is False:
        raise ValueError("Data name is mispelled or does not exist")

    liste_possible = [list(dict_data_source.keys())[i] for i in res]
    liste_possible = {l: dict_data_source[l] for l in liste_possible}
    return liste_possible



# deprecated names ----------------

def telechargerFichier(data, date=None, teldir=None):
    warnings.warn("""
        /!\/!\/!\ \n
        telechargerFichier was an experimental name and might be deprecated in the future\n
        Please use the new function name 'download_store_file' instead
    """)
    return download_store_file(data = data, date = date, teldir = None)

def chargerDonnees(telechargementFichier: dict, vars=None):
    warnings.warn("""
        /!\/!\/!\ \n
        chargerDonnees was an experimental name and might be deprecated in the future\n
        Please use the new function name 'load_data_from_schema' instead
    """)
    return load_data_from_schema(telechargementFichier = telechargementFichier, vars=vars)

def telechargerDonnees(data, date, teldir=None,
                       variables_names=None
                       ):
    warnings.warn("""
        /!\/!\/!\ \n
        telechargerDonnees was an experimental name and might be deprecated in the future\n
        Please use the new function name 'load_data' instead
    """)
    return load_data(data = data, date = date, teldir=teldir, variables_names=variables_names)

def millesimesDisponibles(data):
    warnings.warn("""
        /!\/!\/!\ \n
        millesimesDisponibles was an experimental name and might be deprecated in the future\n
        Please use the new function name 'check_year_available' instead
    """)
    return check_year_available(data = data)

