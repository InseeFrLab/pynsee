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
from shutil import copyfile

# READ ALL DATA SOURCES AVAILABLE USING JSON ONLINE FILE -------------------------------

url_data_list = "https://raw.githubusercontent.com/InseeFrLab/DoReMIFaSol/master/data-raw/liste_donnees.json"
jsonfile = requests.get(url_data_list).json()

# HACK BECAUSE OF DUPLICATED ENTRIES -------------------------------

potential_keys = [items['nom'] for items in jsonfile]
list_duplicated_sources = list(set([x for x in potential_keys if potential_keys.count(x) > 1]))

def create_key(item,list_duplicated_sources):
  if item['nom'] not in list_duplicated_sources:
    return item['nom']
  dateref = item["date_ref"]
  year = re.search(r'\d{4}', dateref).group(0)
  return '{}_{}'.format(item['nom'], year)

dict_data_source = {create_key(item, list_duplicated_sources): item for item in jsonfile} 

#data = "FILOSOFI_AU2010"
#date = "dernier"
#teldir = None
#telechargerFichier("RP_LOGEMENT", date = "2016")

def telechargerFichier(data, date = None, teldir = None):

  caract = info_donnees(data, date)
  if teldir is None:
    cache = True
    tf = tempfile.NamedTemporaryFile(delete=False)
    teldir = tempfile.TemporaryDirectory()
    Path(teldir.name).mkdir(parents=True, exist_ok=True)
  else:
    Path(teldir).mkdir(parents=True, exist_ok=True)

  # IF DOES NOT USE API REST ------

  # filename = "{}/{}".format(teldir.name, os.path.basename(caract['lien']))
  filename = tf.name


  r = requests.get(caract['lien'])
  if r.status_code == 200:
    open(filename, 'wb').write(r.content)
  else:
    raise ValueError("File not found on insee.fr. Please open an issue on https://github.com/InseeFrLab/Py-Insee-Data to help improving the package")


  if hashlib.md5(open(filename, 'rb').read()).hexdigest() != caract['md5']:
    warnings.warn("File in insee.fr modified or corrupted during download")

  if cache:
    print("No destination directory defined. Data have been written there: {}".format(
      filename
    ))
  else:
    print("File has been written there : {}".format(
      filename
    ))

  if caract["zip"] is True:
    fileArchive = filename
    fichierAImporter = "{}/{}".format(tempfile.gettempdir(), caract['fichier_donnees'])
  else:
    fileArchive = None
    fichierAImporter = filename

  argsImport = {"file": fichierAImporter}

  if caract['type'] == "csv":
    argsImport.update({"delim": caract['separateur'], "col_names": True})
    if ('encoding' in list(caract.keys())):
      argsImport.update({"locale": caract["encoding"]})
  elif (caract['type'] in ["xls", "xlsx"]) :
    argsImport.update({'path': fichierAImporter, "skip" : caract['premiere_ligne'] - 1, "sheet" : caract['onglet']})
    if ('derniere_ligne' in list(caract.keys())):
      argsImport.update({"n_max": caract["derniere_ligne"] - caract["premiere_ligne"]})
    else:
      argsImport.update({"n_max": None})
      

    if ('valeurs_manquantes' in list(caract.keys())):
        argsImport.update({"na": caract["valeurs_manquantes"]})

  if 'type_col' in list(caract.keys()):
    list_cols = caract["type_col"]
    for key, value in list_cols.items():
        if value == "character":
          list_cols[key] = "str"
        elif value == "integer":
          list_cols[key] = "int"
  else:
    list_cols = None
  
  argsImport.update({"dtype": list_cols})

  return {"result": caract, 'fileArchive': fileArchive, 'fichierAImporter': fichierAImporter, 'argsImport': argsImport}


def chargerDonnees(telechargementFichier: dict, vars = None):

  if telechargementFichier["result"]["zip"] is True:
#    if telechargementFichier["result"]["big_zip"] is False:
    with zipfile.ZipFile(telechargementFichier['fileArchive'],"r") as zip_ref:
      zip_ref.extractall("{}_temp".format(telechargementFichier["argsImport"]['file']))
    # hack because we unzip whole dir
    copyfile("{}_temp/{}".format(telechargementFichier["argsImport"]['file'], telechargementFichier["result"]['fichier_donnees']),
          telechargementFichier["argsImport"]['file'])  
#    else:
#      with zipfile.ZipFile(telechargementFichier['fileArchive'],"r") as zip_ref:
#        zip_ref.extractall("{}_temp".format(telechargementFichier["argsImport"]['file']))
#    copyfile("{}_temp/{}".format(telechargementFichier["argsImport"]['file'], telechargementFichier["result"]['fichier_donnees']),
#          telechargementFichier["argsImport"]['file'])  


  #    raise ValueError("Not yet implemented")

  if os.path.isfile(telechargementFichier["fichierAImporter"]) is False:
    raise ValueError("File cannot be found")


  if telechargementFichier["result"]["type"] == "csv":
    df = pd.read_csv(telechargementFichier["fichierAImporter"],
        delimiter=telechargementFichier["argsImport"]["delim"],
        dtype=telechargementFichier["argsImport"]["dtype"],
        usecols = vars 
    )
  elif telechargementFichier["result"]["type"] in ["xls", "xlsx"]:
    df = pd.read_excel(telechargementFichier["fichierAImporter"],
      sheet_name = telechargementFichier["argsImport"]["sheet"],
      skiprows = telechargementFichier["argsImport"]["skip"],
      nrows = telechargementFichier["argsImport"]["n_max"],
      na_values = telechargementFichier["argsImport"]["na"],
      dtype = telechargementFichier["argsImport"]["dtype"],
      usecols = vars
      )
  elif telechargementFichier["result"]["type"] == "JSON":
    raise ValueError("Not yet implemented")

  return df


def info_donnees(data, date = None):

  donnees = data.upper()
  liste_nom = dict_data_source.keys()
  liste_nom_no_suffix = [re.sub(r'_\d{4}$','', x) for x in liste_nom]
  res = [i for i, x in enumerate(liste_nom_no_suffix) if x == donnees]

  if not len(res) :
  # looking for close match (Levenshtein distance)
    dist = dict(zip(liste_nom_no_suffix,[lev(donnees, l) for l in liste_nom_no_suffix]))
    suggestions = []
    for key, value in dist.items():
        if value < 6: suggestions += ['\"{}\"'.format(key)]
    if suggestions:
      error_message = "Data name is mispelled, potential values are: {}".format(", ".join(suggestions))
    else:
      error_message = "No data found. Did you mispelled ?"
    raise ValueError(error_message)

  # 2 - gestion millésimes

  possible = millesimesDisponibles(donnees)

  if (len(possible) > 1) & (date is None):
    raise ValueError("Several versions of this dataset exist, please specify a year")

  if date == "dernier":
    latest = sorted(possible.keys(), key=lambda x:x.lower(), reverse=True)[0]
    possible = possible[latest]
  elif date is not None :
    possible = possible["{}_{}".format(donnees, str(date))]

  return possible



def millesimesDisponibles(data):
  
  donnees = data.upper()
  liste_nom = dict_data_source.keys()
  liste_nom_no_suffix = [re.sub(r'_\d{4}$','', x) for x in liste_nom]
  res = [i for i, x in enumerate(liste_nom_no_suffix) if x == donnees]
  
  if res is False:
    raise ValueError("Data name is mispelled or does not exist")
  
  liste_possible = [list(dict_data_source.keys())[i] for i in res]
  liste_possible = {l: dict_data_source[l] for l in liste_possible}
  return liste_possible
