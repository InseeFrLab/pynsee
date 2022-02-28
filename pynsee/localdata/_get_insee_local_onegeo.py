# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import pandas as pd
import numpy as np

from pynsee.utils._request_insee import _request_insee


@lru_cache(maxsize=None)
def _get_insee_local_onegeo(variables, dataset_version, nivgeo, codegeo):

    count_sep = variables.count('-')
    modalite = '.all' * (count_sep + 1)

    link = 'https://api.insee.fr/donnees-locales/V0.1/donnees/'
    link = link + \
        'geo-{}@{}/{}-{}{}'.format(variables,
                                   dataset_version, nivgeo, codegeo, modalite)

    request = _request_insee(
        api_url=link, file_format='application/json;charset=utf-8')

    try:

        data_request = request.json()

        # if 'Cellule' in list(data_request.keys()):
        Cellule = data_request['Cellule']
        Variable = data_request['Variable']
        Croisement = data_request['Croisement']
        Zone = data_request['Zone']

        dataset_version = Croisement['JeuDonnees']['@code']
        dataset_name = Croisement['JeuDonnees']['Source']
        data_date = Croisement['JeuDonnees']['Annee']
        geo_date = Zone['Millesime']['@annee']
        codegeo_label = Zone['Millesime']['Nccenr']

        list_data = []

        for i in range(len(Cellule)):
            dico = {**Cellule[i]['Zone'], **Cellule[i]['Mesure']}
            modalite = Cellule[i]['Modalite']

            for m in range(len(modalite)):
                try:
                    dico_added = {modalite[m]
                                  ['@variable']: modalite[m]['@code']}
                except:
                    dico_added = {modalite['@variable']: modalite['@code']}
                dico = {**dico, **dico_added}

            dico['OBS_VALUE'] = Cellule[i]['Valeur']
            df = pd.DataFrame(dico, index=[0])
            list_data.append(df)

        data = pd.concat(list_data)

        try:
            for i in range(len(Variable)):

                try:
                    df = pd.DataFrame(Variable[i]['Modalite'], index=[0])
                except:
                    list_dict_var = []
                    values = Variable[i]['Modalite']
                    for d in range(len(values)):
                        df_dict = pd.DataFrame(values[d], index=[0])
                        list_dict_var.append(df_dict)
                    df = pd.concat(list_dict_var).reset_index(drop=True)

                var_name = Variable[i]['@code']
                df = df[['@code', 'Libelle']]
                df.columns = [var_name, var_name + '_label']
                data = data.merge(df, on=var_name, how='left')
        except:
            try:
                var_name = Variable['@code']
                var_name_label = var_name + '_label'
                value = Variable['Modalite']['@code']
                label = Variable['Modalite']['Libelle']
                df = pd.DataFrame(
                    {var_name: value, var_name_label: label}, index=[0])
                data = data.merge(df, on=var_name, how='left')
            except:
                var_name = Variable['@code']
                var_name_label = var_name + '_label'

                list_dict_var = []
                values = Variable['Modalite']
                for d in range(len(values)):
                    df_dict = pd.DataFrame(values[d], index=[0])
                    list_dict_var.append(df_dict)
                df = pd.concat(list_dict_var).reset_index(drop=True)
                df = df[['@code', 'Libelle']]
                df.columns = [var_name, var_name_label]
                data = data.merge(df, on=var_name, how='left')

        data = data.assign(DATASET_VERSION=dataset_version,
                           DATASET_NAME=dataset_name,
                           DATA_DATE=data_date,
                           GEO_DATE=geo_date,
                           CODEGEO_label=codegeo_label)

        data.rename(columns={'@codgeo': 'CODEGEO',
                             '@nivgeo': 'NIVGEO',
                             '@code': 'UNIT',
                             '$': 'UNIT_label_fr'}, inplace=True)

        data['OBS_VALUE'] = pd.to_numeric(data['OBS_VALUE'])

    except:
        data = pd.DataFrame(
            {'CODEGEO': codegeo, 'OBS_VALUE': np.nan}, index=[0])

    return(data)
