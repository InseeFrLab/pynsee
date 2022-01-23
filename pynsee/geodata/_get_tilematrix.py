# -*- coding: utf-8 -*-

from re import search
import pandas as pd
import xml.etree.ElementTree as ET
from functools import lru_cache

from pynsee.utils._clean_str import _clean_str
from pynsee.geodata._get_capabilities import _get_capabilities


@lru_cache(maxsize=None)
def _get_tilematrix(key, version, service):
    
    # key = 'economie'
    # version= '1.0.0'
    # service = 'WMTS'

    raw_data_file = _get_capabilities(
        key=key, version=version, service=service.lower())

    root = ET.parse(raw_data_file).getroot()

    if service == 'WMTS':
        list_var = ['Contents']

    find = False

    for i in range(len(root)):
        for var in list_var:
            if _clean_str(root[i].tag) == var:
                data = root[i]
                break
                find = True
        if find:
            break

    n_tilematrix = len(data)

    list_df = []

    for i in range(n_tilematrix):

        df = data[i]

        if search('TileMatrixSet', df.tag):

            TileMatrixSetIdentifier = df[0].text
            TileMatrixSetSupportedCRS = df[1].text

            for t in range(len(df)):

                if search('TileMatrix', df[t].tag):
                    d = {
                        'TileMatrixSetIdentifier': TileMatrixSetIdentifier,
                        'TileMatrixSetSupportedCRS': TileMatrixSetSupportedCRS,
                        'TileMatrixIdentifier': df[t][0].text,
                        'ScaleDenominator': df[t][1].text,
                        'TopLeftCorner': df[t][2].text,
                        'TileWidth': df[t][3].text,
                        'TileHeight': df[t][4].text,
                        'MatrixWidth': df[t][5].text,
                        'MatrixHeight': df[t][6].text}

                    df_matrix = pd.DataFrame(d, index=[0])

                    list_df.append(df_matrix)

    data_all = pd.concat(list_df).reset_index(drop=True)

    newcol_names = ['TopLeftCornerX', 'TopLeftCornerY']

    newcol = pd.DataFrame(data_all.TopLeftCorner.str.split(' ').tolist(),
                          columns=newcol_names)

    data_final = pd.concat([data_all.reset_index(drop=True),
                            newcol], axis=1)

    list_col_convert = ['ScaleDenominator', 'TileHeight', 'TileWidth',
                        'MatrixHeight', 'MatrixWidth'] + newcol_names

    for c in list_col_convert:
        data_final[c] = pd.to_numeric(data_final[c])

    # WMTS standard, 1 pixel = 0.28mm x 0.28mm
    data_final['Resolution'] = data_final['ScaleDenominator'] * 0.28 / 1000

    # 1 tile = 256 pixels
    data_final['TileSize'] = data_final['Resolution'] * 256

    return(data_final)
