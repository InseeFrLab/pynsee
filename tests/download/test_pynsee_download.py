import unittest
import os
import pandas as pd
from parameterized import parameterized

# from pynsee.download import *
from pynsee.download._check_url import _check_url
from pynsee.download import download_file
from pynsee.download import get_file_list
from pynsee.download import get_column_metadata
from pynsee.utils.clear_all_cache import clear_all_cache

# manual commands for testing only on geodata module
# coverage run -m unittest tests/geodata/test_pynsee_geodata.py
# coverage report --omit=*/utils/*,*/macrodata/*,*/localdata/*,*/download/*,*/sirene/*,*/metadata/* -m


class MyTests(unittest.TestCase):

    def test_check_url(self):
        url = "https://www.insee.fr/fr/statistiques/fichier/2540004/nat2020_csv.zip"
        url2 = _check_url(url)
        self.assertTrue(isinstance(url2, str))

    def test_get_file_list_error(self):

        os.environ["pynsee_file_list"] = (
            "https://raw.githubusercontent.com/"
            + "InseeFrLab/DoReMIFaSol/master/data-raw/test.json"
        )

        clear_all_cache()
        df = get_file_list()
        clear_all_cache()
        del os.environ["pynsee_file_list"]

        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_download_big_file(self):
        df = download_file(
            "RP_LOGEMENT_2017",
            variables=["COMMUNE", "IRIS", "ACHL", "IPONDL"],
        )
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_file_list(self):
        meta = get_file_list()
        self.assertTrue(isinstance(meta, pd.DataFrame))

    list_file_check = [
        "COG_COMMUNE_2018",
        "TAG_COM_2025",
        "FILOSOFI_COM_2015",
        "DECES_2020",
        "PRENOM_NAT",
        "ESTEL_T201_ENS_T",
        "FILOSOFI_DISP_IRIS_2017",
        "BPE_ENS",
        "RP_MOBSCO_2016",
        "RP_MOBSCO_2021",  # parquet format
    ]

    @parameterized.expand([[f] for f in list_file_check])
    def test_download(self, f):

        df = download_file(f, update=True)
        label = get_column_metadata(id=f)

        if label is None:
            checkLabel = True
        elif isinstance(label, pd.DataFrame):
            checkLabel = True
        else:
            checkLabel = False

        self.assertTrue(checkLabel)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue((len(df.columns) > 2))

    def test_latest_tag(self):
        """
        test only that 'latest' is working, this does not need to force update
        """
        df = download_file("TAG_COM_LATEST")
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertTrue((len(df.columns) > 2))


if __name__ == "__main__":
    unittest.main()
