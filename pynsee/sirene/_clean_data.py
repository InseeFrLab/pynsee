# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd

from pynsee.metadata.get_activity_list import get_activity_list
from pynsee.metadata.get_legal_entity import get_legal_entity
from pynsee.sirene._employee_metadata import _employee_metadata
from pynsee.sirene._street_metadata import _street_metadata
from pynsee.utils._move_col_after import _move_col_after

# @lru_cache(maxsize=None)


def _clean_data(data_final, kind='siren', clean=True,
                activity=True, legal=True, only_alive=True):

    # try:
    # add activity metadata
    if data_final is not None:
        if activity:
            naf5 = get_activity_list("NAF5")
            naf5 = naf5[["NAF5", "TITLE_NAF5_FR"]]

            if "activitePrincipaleUniteLegale" in data_final.columns:

                naf5_merge = naf5.rename(columns={"NAF5": "activitePrincipaleUniteLegale",
                                                  "TITLE_NAF5_FR": "activitePrincipaleUniteLegaleLibelle"})
                data_final = data_final.merge(
                    naf5_merge, on="activitePrincipaleUniteLegale", how="left")

            if "activitePrincipaleEtablissement" in data_final.columns:

                naf5_merge = naf5.rename(columns={"NAF5": "activitePrincipaleEtablissement",
                                                  "TITLE_NAF5_FR": "activitePrincipaleEtablissementLibelle"})
                data_final = data_final.merge(
                    naf5_merge, on="activitePrincipaleEtablissement", how="left")

        # remove companies which no longer exist
        if only_alive:
            if 'dateFin' in data_final.columns:
                data_final = data_final[data_final['dateFin'].isnull()]
            if 'etatAdministratifEtablissement' in data_final.columns:
                data_final = data_final[data_final['etatAdministratifEtablissement'] == "A"]
            if 'etatAdministratifUniteLegale' in data_final.columns:
                data_final = data_final[data_final['etatAdministratifUniteLegale'] == "A"]

        # add legal entities title
        if legal:
            if 'categorieJuridiqueUniteLegale' in data_final.columns:
                try:
                    list_legal_code = data_final.categorieJuridiqueUniteLegale.unique()
                    data_legal = get_legal_entity(
                        list_legal_code, print_err_msg=False)
                    data_legal = data_legal[['code', 'title']]
                    data_legal = data_legal.rename(columns={'code': 'categorieJuridiqueUniteLegale',
                                                            'title': 'categorieJuridiqueUniteLegaleLibelle'})
                    data_final = data_final.merge(
                        data_legal, on='categorieJuridiqueUniteLegale', how='left')
                except:
                    pass
        # empty columns at the end
        list_all_na_col = [col for col in data_final.columns if all(
            pd.isna(data_final[col]))]
        list_first_col = [
            col for col in data_final.columns if col not in list_all_na_col]
        data_final = data_final[list_first_col + list_all_na_col]

        # change colummn order
        if kind == 'siren':
            first_col = ['siren', 'denominationUniteLegale',
                         'dateFin', 'dateDebut', 'categorieEntreprise',
                         'categorieJuridiqueUniteLegale', 'activitePrincipaleUniteLegale']

        if kind == 'siret':
            first_col = ['siren', 'nic', 'siret', 'dateDebut', 'dateCreationEtablissement',
                         'dateCreationUniteLegale', 'dateFin',
                         'denominationUniteLegale', 'nomUniteLegale',
                         'prenomUsuelUniteLegale',
                         'categorieEntreprise',
                         'categorieJuridiqueUniteLegale',
                         'activitePrincipaleUniteLegale',
                         'activitePrincipaleEtablissement',
                         'numeroVoieEtablissement',
                         'typeVoieEtablissement',
                         'libelleVoieEtablissement', 'codePostalEtablissement',
                         'libelleCommuneEtablissement', 'codeCommuneEtablissement']

        if set(first_col).issubset(data_final.columns):
            other_col = [col for col in data_final if col not in first_col]
            data_final = data_final[first_col + other_col]

        # add employee range metadata
        df_empl_siren = _employee_metadata(kind='siren')
        df_empl_siret = _employee_metadata(kind='siret')

        if 'trancheEffectifsUniteLegale' in data_final.columns:
            data_final = data_final.merge(
                df_empl_siren, on='trancheEffectifsUniteLegale', how='left')

        if 'trancheEffectifsEtablissement' in data_final.columns:
            data_final = data_final.merge(
                df_empl_siret, on='trancheEffectifsEtablissement', how='left')

        # add street metadata
        df_street = _street_metadata()
        if 'typeVoieEtablissement' in data_final.columns:
            data_final = data_final.merge(
                df_street, on='typeVoieEtablissement', how='left')

        # move columns title after columns containing values
        for var in ['categorieJuridiqueUniteLegale',
                    'activitePrincipaleUniteLegale',
                    'activitePrincipaleEtablissement',
                    'typeVoieEtablissement']:

            data_final = _move_col_after(data_final, var + 'Libelle', var)

        for k in ['Etablissement', 'UniteLegale']:
            data_final = _move_col_after(
                data_final, 'effectifsMax' + k, 'trancheEffectifs' + k)
            data_final = _move_col_after(
                data_final, 'effectifsMin' + k, 'trancheEffectifs' + k)

        if clean:
            data_final = data_final.dropna(axis=1, how='all')
    # except:
        # print('\n!!! Error : Data cleaning and harmonization failed !!!')
        # raise ValueError('\n!!! Error : Data cleaning and harmonization failed !!!')

    return(data_final)
