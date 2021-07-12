import os
import requests
import json
from Levenshtein import distance as lev

url_data_list = "https://raw.githubusercontent.com/InseeFrLab/DoReMIFaSol/master/data-raw/liste_donnees.json"
jsonfile = requests.get(url_data_list).json()

dict_data_source = {words['nom'] : words for words in jsonfile}

donnees = "SIRENE_NODIF"
date = None

def info_donnees(data, date = None):

  donnees = data.upper()
  liste_nom = dict_data_source.keys()
  res = donnees in liste_nom

  if res is False:
  # looking for close match (Levenshtein distance)
    dist = dict(zip(liste_nom,[lev(donnees, l) for l in liste_nom]))
    suggestions = []
    for key, value in dist.items():
        if value < 6: suggestions += ['\"{}\"'.format(key)]
    if suggestions:
      error_message = "Data name is mispelled, potential values are: {}".format(", ".join(suggestions))
    else:
      error_message = "No data found. Did you mispelled ?"
    raise ValueError(error_message)

  # to be continued


def millesimesDisponibles(data):
  donnees = data.upper()
  liste_nom = dict_data_source.keys()
  res = donnees in liste_nom
  if res is False:
    raise ValueError("Data name is mispelled or does not exist")
  liste_possible = dict_data_source[donnees]
  return liste_possible


