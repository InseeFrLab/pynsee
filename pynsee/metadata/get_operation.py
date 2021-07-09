# # -*- coding: utf-8 -*-

# import pandas as pd
# from pynsee.utils._request_insee import _request_insee
# from pynsee.sirene._make_dataframe_from_dict import _make_dataframe_from_dict

# link = "https://api.insee.fr/metadonnees/V1/operations/arborescence?diffuseur=insee.fr"

# r = _request_insee(api_url = link, file_format = 'application/json')

# df_raw = r.json()

# for i in range(len(df_raw)):
#     dict_i = df_raw[i]
#     series = dict_i["series"]

#     list_data = []

#     for j in range(len(series)):

#         jdata = series[j]

#         h = pd.DataFrame(jdata)

#         key_list = [key for key in jdata.keys() if type(jdata[key]) is list]
#         key_not_list = [key for key in jdata.keys() if type(jdata[key]) is not list]

#         newdict = {key : jdata[key] for key in key_not_list}

#         data_other0 = pd.DataFrame(newdict, index=[0])

#         data_from_list = []
#         for key in key_list:
#             df = pd.DataFrame(jdata[key])
#             data_from_list.append(df)

#         if len(data_from_list) !=0:
#             data_from_list = pd.concat(data_from_list).reset_index(drop=True)

#             list_data_other = []
#             for i in range(len(data_from_list.index)):
#                 list_data_other.append(data_other0)
#             data_other = pd.concat(list_data_other).reset_index(drop=True)

#             df = pd.concat([data_other, data_from_list], axis=1).reset_index(drop=True)

#         list_data.append(df)

#     data = pd.concat(list_data)
