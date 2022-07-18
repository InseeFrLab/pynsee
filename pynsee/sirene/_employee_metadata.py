# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import pandas as pd


def _employee_metadata(kind="siren"):

    df = pd.DataFrame(
        {
            "trancheEffectifsUniteLegale": [
                "00",
                "01",
                "02",
                "03",
                "11",
                "12",
                "21",
                "22",
                "31",
                "32",
                "41",
                "42",
                "51",
                "52",
                "53",
            ],
            "effectifsMinUniteLegale": [
                0,
                1,
                3,
                6,
                10,
                20,
                50,
                100,
                200,
                250,
                500,
                1000,
                2000,
                5000,
                10000,
            ],
            "effectifsMaxUniteLegale": [
                0,
                2,
                5,
                9,
                19,
                49,
                99,
                199,
                249,
                499,
                999,
                1999,
                4999,
                9999,
                None,
            ],
        }
    )

    if kind == "siret":
        df.columns = [
            "trancheEffectifsEtablissement",
            "effectifsMinEtablissement",
            "effectifsMaxEtablissement",
        ]

    df = df.reset_index(drop=True)

    return df
