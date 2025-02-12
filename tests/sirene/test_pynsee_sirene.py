# Copyright : INSEE, 2021

import pytest

from pandas import pandas as pd

from pynsee.geodata import GeoFrDataFrame
from pynsee.sirene import (
    SireneDataFrame,
    get_dimension_list,
    get_sirene_data,
    get_sirene_relatives,
    search_sirene,
)


def test_get_sirene_relatives():
    df = get_sirene_relatives("00555008200027")
    assert isinstance(df, SireneDataFrame)

    df = get_sirene_relatives(["39860733300059", "00555008200027"])
    assert isinstance(df, SireneDataFrame)

    df = get_sirene_relatives(["39860733300059", "1"])
    assert isinstance(df, SireneDataFrame)


def test_error_get_relatives():
    with pytest.raises(ValueError):
        get_sirene_relatives(1)

    with pytest.raises(ValueError):
        get_sirene_relatives("0")


def test_get_dimension_list():
    df = get_dimension_list()
    assert not df.empty

    df = get_dimension_list("siren")
    assert not df.empty


def test_error_get_dimension_list():
    with pytest.raises(ValueError):
        get_dimension_list("sirène")


def test_get_location():
    df = search_sirene(
        variable=["activitePrincipaleEtablissement"],
        pattern=["29.10Z"],
        kind="siret",
    )

    assert isinstance(df, SireneDataFrame)
    assert not df.empty

    df = search_sirene(
        variable="activitePrincipaleEtablissement",
        pattern="29.10Z",
        kind="siret",
    )
    df = df[:10]
    df = df.reset_index(drop=True)

    sirdf = df.get_location()
    assert isinstance(sirdf, GeoFrDataFrame)

    sirdf = sirdf.loc[~sirdf.geometry.isna()]
    assert not sirdf.empty
    assert all(p.geom_type == "Point" for p in sirdf.geometry)


def test_get_sirene_data():
    df1 = get_sirene_data(["32227167700021", "26930124800077"])
    assert not df1.empty

    df2 = get_sirene_data("552081317")
    assert not df2.empty


def test_error_get_sirene_data():
    with pytest.raises(ValueError):
        get_sirene_data("1")


def test_search_sirene_error():
    def search_sirene_error():
        df = search_sirene(
            kind="test",
            variable=["activitePrincipaleUniteLegale"],
            pattern=["86.10Z", "75*"],
        )
        return df

    pytest.raises(ValueError, search_sirene_error)


def test_search_sirene():
    test = True

    df = search_sirene(
        variable=[
            "activitePrincipaleUniteLegale",
            "codePostalEtablissement",
        ],
        pattern=["86.10Z", "75*|91*"],
        kind="siret",
    )
    test = test & isinstance(df, pd.DataFrame)

    # Test only alive businesses are provided
    test = test & all(df["etatAdministratifEtablissement"] == "A")

    test = test & isinstance(df, pd.DataFrame)

    df = search_sirene(
        variable=[
            "libelleCommuneEtablissement",
            "denominationUniteLegale",
        ],
        pattern=["igny", "pizza"],
        phonetic_search=True,
        number=10,
        kind="siret",
    )
    test = test & isinstance(df, pd.DataFrame)

    # mix of variable with and without history on siren
    # df = search_sirene(variable=["denominationUniteLegale",
    #                              'categorieJuridiqueUniteLegale',
    #                              ],
    #                     number=10,
    #                     closed=True,
    #                     pattern=["sncf", '9220'], kind="siren")
    # test = test & isinstance(df, pd.DataFrame)

    # Test not only alive businesses are provided
    # test = test & (all(df['etatAdministratifUniteLegale'] == "A") is False)

    # input as string and not list
    df = search_sirene(
        variable="libelleCommuneEtablissement",
        number=10,
        pattern="montrouge",
        kind="siret",
    )
    test = test & isinstance(df, pd.DataFrame)

    df = search_sirene(
        variable=[
            "denominationUniteLegale",
            "categorieJuridiqueUniteLegale",
        ],
        pattern=["Pernod Ricard", "5710"],
        number=10,
        kind="siren",
    )
    test = test & isinstance(df, pd.DataFrame)

    # df = search_sirene(variable=["denominationUniteLegale"],
    #                    pattern=["Pernod Ricard"],
    #                    number=10,
    #                    kind="siret")
    # test = test & isinstance(df, pd.DataFrame)

    df = search_sirene(
        variable=["denominationUniteLegale"],
        pattern=["tabac"],
        number=2500,
        kind="siret",
    )
    test = test & isinstance(df, pd.DataFrame)

    # df = search_sirene(variable=['activitePrincipaleEtablissement',
    #                    'codePostalEtablissement'],
    #                    pattern=['56.30Z', '83*'],
    #                    number=100)
    # test = test & isinstance(df, pd.DataFrame)

    df = search_sirene(
        variable=["denominationUniteLegale", "categorieEntreprise"],
        pattern=["Dassot Système", "GE"],
        and_condition=False,
        upper_case=True,
        decode=True,
        update=True,
        phonetic_search=[True, False],
        number=100,
    )
    test = test & isinstance(df, pd.DataFrame)

    assert test


# def test_request_sirene():

#     list_query_siren = ["?q=periode(denominationUniteLegale.phonetisation:sncf)&nombre=20",
#                         '?q=sigleUniteLegale:???&nombre=10',
#                         '?q=periode(activitePrincipaleUniteLegale:86.10Z)&nombre=10']

#     test = True
#     for q in list_query_siren:
#         df = _request_sirene(q, kind='siren')
#         test = test & isinstance(df, pd.DataFrame)

#     list_query_siret = ['?q=denominationUniteLegale.phonetisation:oto&champs=denominationUniteLegale&nombre=10',
#                         # '?q=prenom1UniteLegale:hadrien AND nomUniteLegale:leclerc&nombre=10',
#                         # '?q=prenom1UniteLegale.phonetisation:hadrien AND nomUniteLegale.phonetisation:leclerc&nombre=10',
#                         # '?q=activitePrincipaleUniteLegale:8*&nombre=10',
#                         '?q=activitePrincipaleUniteLegale:86.10Z AND codePostalEtablissement:75*&nombre=10']

#     for q in range(len(list_query_siret)):
#         query = list_query_siret[q]
#         df = _request_sirene(query, kind='siret')
#         test = test & isinstance(df, pd.DataFrame)

#     q = '?q=denominationUniteLegale.phonetisation:Pernod OR denominationUniteLegale.phonetisation:Ricard&nombre=10'
#     df = _request_sirene(q, kind='siret')
#     test = test & isinstance(df, pd.DataFrame)

#     q = '?q=periode(denominationUniteLegale.phonetisation:Dassault) OR periode(denominationUniteLegale.phonetisation:Système) OR categorieEntreprise:GE&nombre=10'
#     df = _request_sirene(q, kind='siren')
#     test = test & isinstance(df, pd.DataFrame)

#     assert test


if __name__ == "__main__":
    test_get_sirene_relatives()
    test_error_get_relatives()
    test_error_get_relatives()
    test_get_dimension_list()
    test_error_get_dimension_list()
    test_get_location()
    test_error_get_sirene_data()
    test_search_sirene_error()
    test_search_sirene()
