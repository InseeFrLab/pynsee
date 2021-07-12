import os
import requests
import json
import re
from Levenshtein import distance as lev


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

