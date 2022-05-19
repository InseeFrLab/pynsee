import unittest
import warnings
import os.path
import hashlib
import pandas as pd

from pynsee.download import *
from pynsee.download import info_data
from pynsee.download import telechargerDonnees
from pynsee.download import load_data
from pynsee.download import check_year_available
from pynsee.download import dict_data_source
from pynsee.download import millesimesDisponibles
from pynsee.download import telechargerFichier


class MyTests(unittest.TestCase):

    # info_data ---------------------------------
        
    def test_levensthein_error_typo(self):
        with self.assertRaises(ValueError):
            info_data("SIRENE_SIRET_NONDIFg")

    def test_levensthein_error_big_typo(self):
        with self.assertRaises(ValueError):
            info_data("randomword")

    def test_info_no_date(self):
        with self.assertRaises(ValueError):
            info_data("FILOSOFI_REG")



    def test_date_info_data_dernier(self):
        self.assertIsInstance(info_data("FILOSOFI_REG", date = "dernier"), dict)

    def test_date_info_data_latest(self):
        self.assertIsInstance(info_data("FILOSOFI_REG", date = "latest"), dict)

    def test_date_info_data_str(self):
        self.assertIsInstance(info_data("FILOSOFI_REG", date = "2016"), dict)

    def test_date_info_data_int(self):
        self.assertIsInstance(info_data("FILOSOFI_REG", date = 2016), dict)

    # def test_nodate(self):
    #   self.assertIsInstance(info_data("SIRENE_SIRET_NONDIFF"), dict)


    # check_year_available -------------------------

    def test_error_check_year_available_typo(self):
        with self.assertRaises(ValueError):
            check_year_available("randomword")

    def test_deprecation_millesimesDisponibles(self):
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always", DeprecationWarning)
            millesimesDisponibles("FILOSOFI_COM")
        self.assertEqual(len(ws), 1)

            

   # def test_keys_json_check_year_available(self):
   #     self.assertEqual([k for k in dict_data_source.keys() if k.startswith("RP_LOGEMENT")],
   #     list(check_year_available("RP_LOGEMENT").keys())
   #     )

    # download_store_file ----------------------------

    def test_error_multiple_data_no_year(self):
        with self.assertRaises(ValueError):
            download_store_file("FILOSOFI_REG")        

    def test_year_string(self):
        filosofi_data = download_store_file("FILOSOFI_REG", date = "2016")
        self.assertIsInstance(filosofi_data, dict)
        self.assertEqual(filosofi_data['result'], dict_data_source["FILOSOFI_REG_2016"])
        path_unzipped = filosofi_data["file_to_import"]
        path_zipped = filosofi_data["file_archive"]
        self.assertTrue(os.path.isfile(path_zipped))
        #self.assertTrue(os.path.isfile(path_unzipped))
        self.assertEqual(filosofi_data["result"]['fichier_donnees'], path_unzipped.split("/")[-1])
        self.assertEqual(hashlib.md5(open(path_zipped, 'rb').read()).hexdigest(), filosofi_data['result']['md5'])


    def test_year_int(self):
        filosofi_data = download_store_file("FILOSOFI_REG", date = 2016)
        self.assertIsInstance(filosofi_data, dict)
        self.assertEqual(filosofi_data['result'], dict_data_source["FILOSOFI_REG_2016"])
        path_unzipped = filosofi_data["file_to_import"]
        path_zipped = filosofi_data["file_archive"]
        self.assertTrue(os.path.isfile(path_zipped))
        #self.assertTrue(os.path.isfile(path_unzipped))
        self.assertEqual(filosofi_data["result"]['fichier_donnees'], path_unzipped.split("/")[-1])
        self.assertEqual(hashlib.md5(open(path_zipped, 'rb').read()).hexdigest(), filosofi_data['result']['md5'])

    def test_year_dernier(self):
        filosofi_data = download_store_file("FILOSOFI_REG", date = "dernier")
        latest = list(check_year_available("FILOSOFI_REG").keys())[-1]
        self.assertIsInstance(filosofi_data, dict)
        self.assertEqual(filosofi_data['result'], dict_data_source[latest])
        path_unzipped = filosofi_data["file_to_import"]
        path_zipped = filosofi_data["file_archive"]
        self.assertTrue(os.path.isfile(path_zipped))
        #self.assertTrue(os.path.isfile(path_unzipped))
        self.assertEqual(filosofi_data["result"]['fichier_donnees'], path_unzipped.split("/")[-1])
        self.assertEqual(hashlib.md5(open(path_zipped, 'rb').read()).hexdigest(), filosofi_data['result']['md5'])

    def test_year_latest(self):
        filosofi_data = download_store_file("FILOSOFI_REG", date = "latest")
        latest = list(check_year_available("FILOSOFI_REG").keys())[-1]
        self.assertIsInstance(filosofi_data, dict)
        self.assertEqual(filosofi_data['result'], dict_data_source[latest])
        path_unzipped = filosofi_data["file_to_import"]
        path_zipped = filosofi_data["file_archive"]
        self.assertTrue(os.path.isfile(path_zipped))
        #self.assertTrue(os.path.isfile(path_unzipped))
        self.assertEqual(filosofi_data["result"]['fichier_donnees'], path_unzipped.split("/")[-1])
        self.assertEqual(hashlib.md5(open(path_zipped, 'rb').read()).hexdigest(), filosofi_data['result']['md5'])


    def test_deprecation_telechargerFichier(self):
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter("always", DeprecationWarning)
            telechargerFichier("FILOSOFI_REG", date = "latest")
        self.assertEqual(len(ws), 1)


    # telechargerDonnees ----------------------------

    # def test_load_data(self):
    #     df = load_data("FILOSOFI_COM", date = "2015")
    #     self.assertIsInstance(df, pd.DataFrame)

    # def test_load_data_no_onglet(self):
    #     df = load_data("FILOSOFI_DISP_COM", date = "dernier")
    #     self.assertIsInstance(df, pd.DataFrame)

    # def test_load_data_FILOSOFI_AU2010(self):
    #     df = load_data("FILOSOFI_AU2010", date = "dernier")
    #     self.assertIsInstance(df, pd.DataFrame)

    #def test_load_data_RPLOGEMENT2016(self):
    #    df = load_data("RP_LOGEMENT", date = "2016")
    #    self.assertIsInstance(df, pd.DataFrame)

    # def test_load_data_estel_2016(self):
    #     df = load_data("AIRE_URBAINE", date = "latest")
    #     self.assertIsInstance(df, pd.DataFrame)
    
    def test_deprecation_notice_telechargerDonnees(self):
        with self.assertWarns(Warning):
            telechargerDonnees("AIRE_URBAINE", date = "latest")      

    def test_equivalence_loaddata_telechargerDonnees(self):
        df1 = telechargerDonnees("AIRE_URBAINE", date = "latest")  
        df2 = load_data("AIRE_URBAINE", date = "latest")
        pd.testing.assert_frame_equal(df1,df2)

        
if __name__ == '__main__':
    unittest.main()


