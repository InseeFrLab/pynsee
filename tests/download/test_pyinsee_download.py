import unittest

from pynsee.download import *

class MyTests(unittest.TestCase):

    # info_donnees ---------------------------------
        
    def test_levensthein_error_typo(self):
        with self.assertRaises(ValueError):
            info_donnees("SIRENE_SIRET_NONDIFg")

    def test_levensthein_error_big_typo(self):
        with self.assertRaises(ValueError):
            info_donnees("randomword")

    def test_info_no_date(self):
        with self.assertRaises(ValueError):
            info_donnees("RP_LOGEMENT")



    def test_date_info_donnees_dernier(self):
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = "dernier"), dict)

    def test_date_info_donnees_latest(self):
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = "latest"), dict)

    def test_date_info_donnees_str(self):
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = "2012"), dict)

    def test_date_info_donnees_int(self):
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = 2012), dict)

    def test_nodate(self):
        self.assertIsInstance(info_donnees("SIRENE_SIRET_NONDIFF"), dict)


    # millesimesDisponibles -------------------------

    def test_error_millesimesDisponibles_typo(self):
        with self.assertRaises(ValueError):
            millesimesDisponibles("randomword")



if __name__ == '__main__':
    unittest.main()

#chargerDonnees(telechargerFichier("ESTEL_T201_ENS_TBE", "dernier"))
#chargerDonnees(telechargerFichier("RP_LOGEMENT", "dernier"))
#telechargerDonnees("RP_LOGEMENT", date = "2016")
#telechargerDonnees("FILOSOFI_AU2010", "dernier")
