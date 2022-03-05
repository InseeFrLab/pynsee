# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import os
import re
import zipfile
import pkg_resources
import pandas as pd

from pynsee.utils._create_insee_folder import _create_insee_folder


@lru_cache(maxsize=None)
def _warning_data():
    print("!!! This function renders only package's internal data,\nit might not be the most up-to-date\nHave a look at api.insee.fr !!!")


@lru_cache(maxsize=None)
def get_local_metadata():
    """Get a list of all combinations of datasets, variables and unit measures available from INSEE Local API

    Examples:
        >>> from pynsee.localdata import get_local_metadata
        >>> metadata = get_local_metadata()
    """
    _warning_data()

    insee_folder = _create_insee_folder()

    insee_folder_local_metadata = insee_folder + '/' + 'local_metadata'

    if not os.path.exists(insee_folder_local_metadata):
        os.mkdir(insee_folder_local_metadata)

    dataset_label = ['Recensement de la population',
                     'Séries historiques du recensement de la population (depuis 1968)',
                     'Populations légales (issue du RP)',
                     "Données de l'état-civil (naissances et décès)",
                     "Répertoire des entreprises et des établissements (issu de Sirene)",
                     "Fichier localisé social et fiscal",
                     "Fichier localisé des rémunérations et de l'emploi salarié",
                     "Tourisme (offre d'hébergement)"
                     ]
    all_files = []
    name_dataset = ['RP', 'BDCOM', 'Popleg', 'RFD',
                    'REE', 'FILOSOFI', 'Flores', 'TOUR']
                    
    var_name = ['var_modalite', 'mesure_croisement', 'lib_mesure', 'millesime']
    for var in var_name:
        for dt in name_dataset:
            all_files.append('doc_' + dt + '_' + var + '.csv')

    list_files = os.listdir(insee_folder_local_metadata)
    list_files = [f for f in list_files if re.search('^doc_.*csv$', f)]

    test_file_available = [f not in list_files for f in all_files]
    #any(test_file_available)
    if True:
        zip_file = pkg_resources.resource_stream(
            __name__, 'data/local_metadata.zip')

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(insee_folder)

    def extract_data_from_excel_sheet(var,
                                      list_col,
                                      reshape=False,
                                      list_files=all_files,
                                      folder=insee_folder_local_metadata):

        list_files = [f for f in list_files if re.search('.*' + var + '.*', f)]

        if reshape is True:
            list_col = ['var' if x == 'variable' else x for x in list_col]

        list_var_data = []

        for f in range(len(list_files)):
            try:
                file2load = folder + '/' + list_files[f]
                df = pd.read_csv(file2load, sep =",", encoding="UTF-8")

                if reshape is True:
                    df.columns = ['var' if x
                                  == 'variable' else x for x in df.columns]

                    list_other_col = [
                        col for col in df.columns if col not in list_col]

                    if len(list_other_col) > 0:
                        list_col2 = [
                            col for col in list_col if col in df.columns]
                        list_col_new2 = list_col2 + ['dataset_value']
                        # reshape dataframe
                        df = pd.melt(df, id_vars=list_col2,
                                     value_vars=list_other_col)
                        # rename col variable into dataset_value
                        df.columns = ['dataset_value' if x
                                      == 'variable' else x for x in df.columns]
                        # drop nan in value col
                        df = df[df['value'].notna()]
                        # drop value column
                        df = df[list_col_new2]

                # add column to reference
                file_id = list_files[f].replace("doc_", "").replace(
                    ".csv", "").replace('_' + var, "")
                df = df.assign(dataset=file_id, tab=var)

            except:
                #  print('error {} {}'.format(list_files[f], var))
                pass
            else:
                list_var_data.append(df)

        var_data = pd.concat(list_var_data)
        return(var_data)

    #
    # get all variables from all datasets
    #

    list_col_mesure_croisement = ['mesure', 'croisement',
                                  'filtre_stat', 'filtre_geo',
                                  'nom_tab', 'filtre_geo_avt_2017', 'type_exploitation']

    mesure_croisement = extract_data_from_excel_sheet(var='mesure_croisement',
                                                      list_col=list_col_mesure_croisement,
                                                      reshape=True)

    variables = mesure_croisement[['croisement',
                                   'mesure', 'dataset_value', 'dataset']]

    #
    # get variables labels
    #
    list_col_var_modalite = ['variable', 'lib_var', 'modalite', 'lib_modalite']

    var_modalite = extract_data_from_excel_sheet(var='var_modalite',
                                                 list_col=list_col_var_modalite,
                                                 reshape=True)

    var_label = var_modalite[['var', 'lib_var']
                             ].drop_duplicates(subset='var', keep='first')
    var_label.columns = ['croisement', 'variable_label']

    #
    # add variable labels to variables list
    #
    variables_splitted = variables['croisement'].str.split('-').tolist()

    variables_splitted = pd.DataFrame(
        variables_splitted, index=variables.index)

    for icol in range(len(variables_splitted.columns)):
        var_label_icol = var_label
        var_label_icol.columns = [icol, 'var_label' + str(icol)]

        variables_splitted = pd.merge(variables_splitted, var_label_icol,
                                      how='left',
                                      on=icol)

    var_labels = variables_splitted.filter(regex='var_label')
    var_labels = var_labels.assign(variables_label="")
    icol_var_label = var_labels.columns.get_loc('variables_label')

    for icol in range(len(var_labels.columns) - 1):
        for irow in range(len(var_labels.index)):
            val = var_labels.iloc[irow, icol]
            if not pd.isna(val):
                if var_labels.iloc[irow, icol_var_label] != "":
                    var_labels.iloc[irow, icol_var_label] = var_labels.iloc[irow,
                                                                            icol_var_label] + ' - ' + str(val)
                else:
                    var_labels.iloc[irow, icol_var_label] = str(val)

    var_labels = var_labels[['variables_label']]
    variables = pd.concat([variables.reset_index(), var_labels], axis=1)

    del variables['index']

    #
    # add metadata on unit (labels) to variables list
    #
    lib_mesure = extract_data_from_excel_sheet(var='lib_mesure',
                                               list_col=['mesure', 'lib_mesure'])

    lib_mesure = lib_mesure[['mesure', 'lib_mesure']]
    lib_mesure = lib_mesure.drop_duplicates()
    variables = variables.merge(lib_mesure, on='mesure', how='left')

    #
    # add metadata on millesime to variables list: geo data date and data date
    #
    millesime = extract_data_from_excel_sheet(var='millesime',
                                              list_col=['jeu_donnees', 'millesime_donnees', 'millesime_geo'])

    millesime = millesime[['jeu_donnees',
                           'millesime_geo', 'millesime_donnees']]
    millesime.columns = ['dataset_value', 'millesime_geo', 'millesime_donnees']
    millesime = millesime.drop_duplicates()

    variables = variables.merge(millesime, on='dataset_value', how='left')

    dataset_dict = {'dataset': name_dataset,
                    'dataset_label': dataset_label}
    datasets = pd.DataFrame(dataset_dict)
    variables = variables.merge(datasets, on='dataset', how='left')

    variables.columns = ['VARIABLES', 'UNIT', 'DATASET_VERSION', 'DATASET',
                         'VARIABLES_label_fr', 'UNIT_label_fr', 'GEO_DATE',
                         'DATA_DATE', 'DATASET_label_fr']

    # variables = variables.dropna(subset=['GEO_DATE'])
    variables = variables[~variables.DATASET_VERSION.str.contains('filtre_geo ')]
    variables = variables.reset_index(drop=True)
    
    return(variables)
