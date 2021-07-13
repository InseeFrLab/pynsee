import warnings
import hashlib
import tempfile
import os
import requests
import json
import re
from Levenshtein import distance as lev
from pathlib import Path

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


data = "COG_REGION"
date = "dernier"
teldir = None

caract = info_donnees(data, date)
if teldir is None:
  cache = True
  teldir = tempfile.TemporaryDirectory()
else:
  Path(teldir).mkdir(parents=True, exist_ok=True)

# IF DOES NOT USE API REST ------

filename = "{}/{}".format(teldir.name, os.path.basename(caract['lien']))


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
  fichierAImporter = "{}/{}".format(teldir, caract['fichier_donnees'])
else:
  fileArchive = None
  fichierAImporter = filename

if caract['type'] == "csv":
  argsImport = {"file": fichierAImporter, "delim": caract['separateur'], "col_names": True}
    
    if (caract$type == "csv") {
      argsImport <- list(file = fichierAImporter, delim = eval(parse(text = caract$separateur)), col_names = TRUE)
      if (!is.null(caract$encoding))
        argsImport[["locale"]] <- readr::locale(encoding = caract$encoding)
      if (!is.null(caract$valeurs_manquantes))
        argsImport[["na"]] <- unlist(strsplit(caract$valeurs_manquantes, "/"))
    } else if (caract$type == "xls") {
      argsImport <- list(path = fichierAImporter, skip = caract$premiere_ligne - 1, sheet = caract$onglet)
      if (!is.null(caract$derniere_ligne))
        argsImport[["n_max"]] <- caract$derniere_ligne - caract$premiere_ligne
      if (!is.null(caract$valeurs_manquantes))
        argsImport[["na"]] <- unlist(strsplit(caract$valeurs_manquantes, "/"))
    } else if (caract$type == "xlsx") {
      argsImport <- list(path = fichierAImporter, sheet = caract$onglet, skip = caract$premiere_ligne - 1)
    }
    
    if (!is.null(caract$type_col)) {
      listvar <- lapply(
        caract$type_col,
        function(x) eval(parse(text = paste0("readr::col_", x, "()")))
      )
      cols <- readr::cols()
      cols$cols <- listvar
      argsImport[["col_types"]] <- cols
    }
    
  } else {
    
    ## télécharge les données sur l'API
    
    if (!nzchar(Sys.getenv("INSEE_APP_KEY")) || !nzchar(Sys.getenv("INSEE_APP_SECRET"))) {
      stop("d\u00e9finir les variables d'environnement INSEE_APP_KEY et INSEE_APP_SECRET")
    }
    
    if (!curl::has_internet()) stop("aucune connexion Internet")
    
    timestamp <- gsub("[^0-9]", "", as.character(Sys.time()))
    dossier_json <- paste0(telDir, "/json_API_", caract$nom, "_", timestamp, "_", genererSuffixe(4))
    dir.create(dossier_json)
    writeLines(
      utils::URLdecode(httr::modify_url(caract$lien, query = argsApi)),
      file.path(dossier_json, "requete.txt")
    )
    
    token <- apinsee::insee_auth()
    if (!is.null(date))
      argsApi <- c(date = as.character(date), argsApi)
    if (is.null(argsApi$nombre)) {
      argsApi[["nombre"]] <- 0
      url <- httr::modify_url(caract$lien, query = argsApi)
      res <- tryCatch(httr::GET(url, httr::config(token = token), 
                                httr::write_memory()),
                      error = function(e) message(e$message))
      total <- tryCatch(httr::content(res)[[1]]$total,
                        error = function(e) return(NULL))
      if (is.null(total))
        total <- 0
    } else {
      total <- argsApi[["nombre"]]
    }
    argsApi[["nombre"]] <- min(total, 1000)
    if (is.null(argsApi[["tri"]]))
      argsApi[["tri"]] <- "siren"
    if (total > 1000)
      argsApi[["curseur"]] <- "*"
    nombrePages <- ceiling(total/1000)
    url <- httr::modify_url(caract$lien, query = argsApi)
    fichierAImporter <- sprintf("%s/results_%06i.json", dossier_json, 1)
    res <- requeteApiSirene(url = url, fichier = fichierAImporter, token = token, 
                            nbTentatives = 400)
    resultat <- res$status_code
    if (nombrePages > 1) {
      for (k in 2:nombrePages) {
        argsApi[["curseur"]] <-httr::content(res)$header$curseurSuivant
        url <- httr::modify_url(caract$lien, query = argsApi)
        fichierAImporter <- c(fichierAImporter, sprintf("%s/results_%06i.json", dossier_json, k))
        res <- requeteApiSirene(url, fichierAImporter, token, 400)
        resultat <- c(resultat, res$status_code)
      }
    }
    dl <- NULL
    if (all(resultat == 200) & total > 0)
      dl <- 0
    argsImport <- list(fichier = fichierAImporter, nom = caract$nom)
    fileArchive <- NULL
    
  }
  
  invisible(
    list(
      result      = dl,
      lien        = caract$lien,
      zip         = caract$zip,
      big_zip     = caract$big_zip,
      fileArchive = fileArchive,
      type        = caract$type,
      argsImport  = argsImport
    )
  )
  
}





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

