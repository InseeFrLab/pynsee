# Copyright : INSEE, 2021

import pandas as pd
import math
from functools import lru_cache

from pynsee.utils._request_insee import _request_insee
from pynsee.sirene._make_dataframe import _make_dataframe


@lru_cache(maxsize=None)
def _request_sirene(query, kind, number=1001, query_limit=20):

    # query = '?q=denominationUniteLegale:pizza'
    # query = '?q=periode(activitePrincipaleEtablissement:56.30Z) AND codePostalEtablissement:83*'
    # kind = 'siret'
    # number = 4500

    if kind == 'siren':
        main_key = 'unitesLegales'
    elif kind == 'siret':
        main_key = 'etablissements'
    else:
        raise ValueError('!!! kind should be among : siren siret !!!')

    INSEE_api_sirene_siren = "https://api.insee.fr/entreprises/sirene/V3"
    number_query_limit = 1000

    number_query = min(number_query_limit, number)

    n_query_total = math.ceil(number / number_query_limit)
    i_query = 1
    query_number = '{}/{}'.format(i_query, n_query_total)

    main_query = INSEE_api_sirene_siren + '/' + kind + query

    link = main_query + "&nombre={}".format(number_query)

    if number > number_query_limit:
        link = link + '&curseur=*'

    request = _request_insee(
        api_url=link, file_format='application/json;charset=utf-8')

    list_dataframe = []

    request_status = request.status_code

    if request_status == 200:

        data_request = request.json()

        data_request_1 = _make_dataframe(data_request, main_key, '1')

        if 'siret' in data_request_1.columns:
            df_nrows = len(data_request_1.siret.unique())
        elif 'siren' in data_request_1.columns:
            df_nrows = len(data_request_1.siren.unique())
        else:
            df_nrows = len(data_request_1.index.unique())

        list_dataframe.append(data_request_1)

        list_header_keys = list(data_request['header'].keys())

        if 'curseur' in list_header_keys:

            cursor = data_request['header']['curseur']
            following_cursor = data_request['header']['curseurSuivant']

            while (following_cursor != cursor) & (request_status == 200) & (df_nrows < number) & (i_query < query_limit):

                i_query += 1
                query_number = '{}/{}'.format(i_query, n_query_total)

                new_query = main_query + \
                    "&nombre={}".format(number_query_limit) + \
                    '&curseur=' + following_cursor

                request_new = _request_insee(
                    api_url=new_query, file_format='application/json;charset=utf-8')

                request_status = request_new.status_code

                if request_status == 200:

                    data_request_new = request_new.json()
                    cursor = data_request_new['header']['curseur']
                    following_cursor = data_request_new['header']['curseurSuivant']
                    # print(f'cursor:{cursor}, next_cursor:{following_cursor}\n')

                    if len(data_request_new[main_key]) > 0:

                        df = _make_dataframe(
                            data_request_new, main_key, query_number)

                        if 'siret' in df.columns:
                            df_nrows += len(df.siret.unique())
                        elif 'siren' in df.columns:
                            df_nrows += len(df.siren.unique())
                        else:
                            df_nrows += len(df.index.unique())

                        list_dataframe.append(df)
                    else:
                        print('{} - No more data found'.format(query_number))

                    if cursor == following_cursor:
                        i_query += 1
                        query_number = '{}/{}'.format(i_query, n_query_total)
                        print('{} - No more data found'.format(query_number))
                    
                    if df_nrows == number:
                        print('!!! maximum reached, increase value of number argument !!!')

                    if i_query == query_limit:
                        print('!!! maximum reached, increase value of query_limit argument !!!')

        data_final = pd.concat(list_dataframe)

        return(data_final)
    else:
        print(request.text)
        return(None)
