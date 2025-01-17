# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import time
from unittest import TestCase
import pandas as pd
import sys
import unittest
import re
import os

from pynsee.localdata._get_geo_relation import _get_geo_relation
from pynsee.localdata._get_insee_one_area import _get_insee_one_area

from pynsee.localdata.get_area_list import get_area_list
from pynsee.localdata.get_geo_list import get_geo_list

from pynsee.localdata.get_local_data import get_local_data
from pynsee.localdata.get_nivgeo_list import get_nivgeo_list
from pynsee.localdata.get_local_metadata import get_local_metadata
from pynsee.localdata.get_population import get_population
from pynsee.localdata.get_old_city import get_old_city
from pynsee.localdata.get_new_city import get_new_city
from pynsee.localdata.get_area_projection import get_area_projection
from pynsee.localdata.get_ascending_area import get_ascending_area
from pynsee.localdata.get_descending_area import get_descending_area

# manual commands for testing only on geodata module
# coverage run -m unittest tests/geodata/test_pynsee_geodata.py
# coverage report --omit=*/utils/*,*/macrodata/*,*/localdata/*,*/download/*,*/sirene/*,*/metadata/* -m


class TestFunction(TestCase):

    # version = (sys.version_info[0] == 3) & (sys.version_info[1] == 9)

    # test_onyxia = re.match(".*onyxia.*", os.getcwd())
    # version = version or test_onyxia

    # if version:

    def test_get_population(self):
        df = get_population()
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_insee_one_area_1(self):
        def get_insee_one_area_test(area_type="derf", codearea="c"):
            _get_insee_one_area(area_type=area_type, codearea=codearea)

        self.assertRaises(ValueError, get_insee_one_area_test)

    def test_get_insee_one_area_2(self):
        def get_insee_one_area_test(area_type="ZoneDEmploi2020", codearea="c"):
            _get_insee_one_area(area_type=area_type, codearea=codearea)

        self.assertRaises(ValueError, get_insee_one_area_test)

    def test_get_new_city(self):
        test = True
        df = get_new_city(code="24431", date="2018-01-01")
        test = test & isinstance(df, pd.DataFrame)
        # df = get_new_city(code="24431")
        # test = test & isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    # def test_get_area_projection1(self):
    #     test = True
    #     df = get_area_projection(
    #         area="commune", code="01039", date="2020-01-01"
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     test = test & (df.loc[0, "code"] == "01138")
    #     self.assertTrue(test)

    def test_get_area_projection2(self, test=True):

        df = get_area_projection(
            area="commune",
            code="01039",
            date="2020-01-01",
            dateProjection="1900-01-01",
        )
        test = test & isinstance(df, pd.DataFrame) & (len(df.index) == 0)
        self.assertTrue(test)

    # def test_get_area_projection3(self, test=True):

    #     df = get_area_projection(
    #         area="commune",
    #         code="01039",
    #         date="2020-01-01",
    #         dateProjection="2023-04-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     test = test & (df.loc[0, "code"] == "01138")
    #     self.assertTrue(test)

    # def test_get_area_projection4(self, test=True):

    #     df = get_area_projection(
    #         area="commune",
    #         code="01039",
    #         date="2020-01-01",
    #         dateProjection="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     test = test & (df.loc[0, "code"] == "01039")
    #     self.assertTrue(test)

    # def test_get_area_projection5(self, test=True):

    #     df = get_area_projection(
    #         area="departement",
    #         code="01",
    #         date="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     self.assertTrue(test)

    # def test_get_area_projection6(self, test=True):

    #     df = get_area_projection(
    #         area="arrondissement",
    #         code="011",
    #         date="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     self.assertTrue(test)

    # def test_get_area_projection7(self, test=True):

    #     df = get_area_projection(
    #         area="arrondissementmunicipal",
    #         code="75113",
    #         date="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     self.assertTrue(test)

    # def test_get_area_projection8(self, test=True):

    #     df = get_area_projection(
    #         area="arrondissementMunicipal",
    #         code="75113",
    #         date="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     self.assertTrue(test)

    # def test_get_area_projection9(self, test=True):

    #     df = get_area_projection(
    #         area="region",
    #         code="32",
    #         date="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     self.assertTrue(test)

    # def test_get_area_projection10(self, test=True):

    #     df = get_area_projection(
    #         area="intercommunalite",
    #         code="200046977",
    #         date="2020-01-01",
    #     )
    #     test = test & isinstance(df, pd.DataFrame)
    #     self.assertTrue(test)

    # def test_get_area_projection_dummy(self):
    #     self.assertRaises(
    #         ValueError,
    #         get_area_projection,
    #         "dummy",
    #         "32",
    #         "2020-01-01",
    #     )

    def test_get_old_city(self):

        df = get_old_city(code="24259")

        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_geo_list_1(self):
        list_available_geo = [
            "communes",
            "regions",
            "departements",
            # "communesDeleguees",
            # "communesAssociees",
            # "arrondissements",
            # "arrondissementsMunicipaux",
        ]

        list_geo_data = []
        for geo in list_available_geo:
            # time.sleep(1)
            self.assertTrue(isinstance(get_geo_list(geo), pd.DataFrame))
            # list_geo_data.append()

        # df = pd.concat(list_geo_data)

        # repeat test to check locally saved data use
        # self.assertTrue(isinstance(get_geo_list("regions"), pd.DataFrame))

    def test_get_geo_list_2(self):
        self.assertRaises(ValueError, get_geo_list, "a")

    # def test_get_geo_relation_1(self):
    #     df1 = _get_geo_relation("region", "11", "descendants")
    #     time.sleep(1)
    #     df2 = _get_geo_relation("departement", "91", "ascendants")
    #     test = isinstance(df1, pd.DataFrame) & isinstance(
    #         df2, pd.DataFrame
    #     )
    #     self.assertTrue(test)

    def test_get_nivgeo_list(self):
        data = get_nivgeo_list()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_local_metadata(self):
        data = get_local_metadata()
        self.assertTrue(isinstance(data, pd.DataFrame))

    # def test_get_local_data_1(self):
    #     # dep = get_geo_list("departements")

    #     variables = "AGESCOL-SEXE-ETUD"
    #     dataset = "GEO2019RP2011"
    #     codegeos = ['91', '976']
    #     # codegeos = list(dep.CODE)
    #     # codegeos = dep.CODE.to_list()
    #     geo = "DEP"
    #     data = get_local_data(
    #         variables=variables,
    #         dataset_version=dataset,
    #         nivgeo=geo,
    #         geocodes=codegeos,
    #     )

    #     self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_local_data_all(self):
        test = True

        data = get_local_data(
            dataset_version="GEO2020RP2017",
            variables="SEXE-DIPL_19",
            nivgeo="DEP",
            geocodes=["91", "976"],
            update=True,
        )
        test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(
        #     dataset_version="GEO2020FILO2018",
        #     variables="INDICS_FILO_DISP_DET-TRAGERF",
        #     nivgeo="REG",
        #     geocodes=["01", "11"],
        #     update=True
        # )
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(
        #     dataset_version="BDCOM2017",
        #     variables="INDICS_BDCOM",
        #     nivgeo="REG",
        #     geocodes=["11"],
        #     update=True
        # )
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(
        #     dataset_version="GEO2019RFD2011",
        #     variables="INDICS_ETATCIVIL",
        #     nivgeo="REG",
        #     geocodes=["11"],
        #     update=True
        # )
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(
        #     dataset_version="TOUR2019",
        #     variables="ETOILE",
        #     nivgeo="REG",
        #     geocodes=["11"],
        #     update=True
        # )
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(
        #     dataset_version="GEO2019REE2018",
        #     variables="NA5_B",
        #     nivgeo="REG",
        #     geocodes=["11"],
        #     update=True
        # )
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(
        #     dataset_version="POPLEG2018",
        #     variables="IND_POPLEGALES",
        #     nivgeo="COM",
        #     geocodes=["91477"],
        #     update=True
        # )
        # test = test & isinstance(data, pd.DataFrame)

        # for geo in ["DEP", "REG", "FE", "METRODOM"]:
        #     data = get_local_data(
        #         dataset_version="GEO2020FLORES2017",
        #         variables="NA17",
        #         nivgeo=geo,
        #         update=True
        #     )
        # test = test & isinstance(data, pd.DataFrame)

        self.assertTrue(test)

    def test_get_local_data_latest(self):
        test = True
        # data = get_local_data(
        #     dataset_version="GEOlatestRPlatest", variables="CS1_6"
        # )
        # test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEOlatestRPlatest",
            variables="TF4",
            nivgeo="COM",
            geocodes=["75056"],
        )
        test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(dataset_version='GEOlatestFILOlatest',
        #            variables =  'INDICS_FILO_DISP',
        #            nivgeo = 'COM',
        #            update=True,
        #            geocodes = '75056')
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(dataset_version='POPLEGlatest',
        #            variables =  'IND_POPLEGALES',
        #            nivgeo = 'COM',
        #            update=True,
        #            geocodes = '75056')
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(dataset_version='GEOlatestRFDlatest',
        #            variables =  'INDICS_ETATCIVIL',
        #            nivgeo = 'COM',
        #            update=True,
        #            geocodes = '75056')
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(dataset_version='BDCOMlatest',
        #            variables =  'INDICS_BDCOM',
        #            nivgeo = 'COM',
        #            update=True,
        #            geocodes = '75056')
        # test = test & isinstance(data, pd.DataFrame)

        # data = get_local_data(dataset_version='GEOlatestREElatest',
        #            variables =  'NA10_HORS_AZ-ENTR_INDIVIDUELLE',
        #            nivgeo = 'COM',
        #            update=True,
        #            geocodes = '75056')
        # test = test & isinstance(data, pd.DataFrame)

        self.assertTrue(test)

    def test_get_ascending_descending_area(self):
        #
        # test get_descending_area and get_ascending_are
        #
        test = True
        df = get_descending_area("commune", code="59350", date="2018-01-01")
        test = test & isinstance(df, pd.DataFrame)

        df = get_descending_area("departement", code="59")
        test = test & isinstance(df, pd.DataFrame)

        # df = get_descending_area("zoneDEmploi2020", code="1109")
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_ascending_area("commune", code="59350", date="2018-01-01")
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_descending_area(
        #     "departement", code="59", type="arrondissement", update=True
        # )
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_descending_area(
        #     "departement", code="59", type="arrondissement", update=False
        # )
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_ascending_area("commune", code="59350", date="2018-01-01")
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_ascending_area("departement", code="59")
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_ascending_area(
        #     "departement", code="59", type="region", update=True
        # )
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_ascending_area("commune", code="59350", date="2018-01-01")
        # test = test & isinstance(df, pd.DataFrame)

        self.assertTrue(test)

    def test_get_local_data_latest_error(self):
        def getlocaldataTestError():
            data = get_local_data(
                dataset_version="GEOlatestTESTlatest", variables="CS1_6"
            )
            return data

        self.assertRaises(ValueError, getlocaldataTestError)

    def test_get_area_list_1(self):
        test = True

        df = get_area_list(update=True)
        test = test & isinstance(df, pd.DataFrame)

        # df = get_area_list(update=False)
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_area_list(area="collectivitesDOutreMer", update=True)
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_area_list(area="UU2020", update=True)
        # test = test & isinstance(df, pd.DataFrame)

        # df = get_area_list(area="regions", date="2023-01-01", update=True)
        # test = test & isinstance(df, pd.DataFrame)

        # self.assertTrue(test)

    # def test_get_area_list_2(self):
    #     def get_area_list_test():
    #         get_area_list("a")
    #     self.assertRaises(ValueError, get_area_list_test)

    # def test_get_area_list_3(self):
    #     def get_area_list_test():
    #         get_area_list(area="regions", date="1900-01-01", update=True)
    #     self.assertRaises(RequestException, get_area_list_test)


if __name__ == "__main__":
    unittest.main()
    # TestFunction().test_get_local_metadata()
