import unittest

from pynsee.download import *

class MyTestCase(unittest.TestCase):
    def test_levensthein_error(self):
        self.assertRaises(ValueError, info_donnees, data = "SIRENE_SIRET_NONDIFg")
        self.assertRaises(ValueError, info_donnees, data = "randomword")
        self.assertRaises(ValueError, info_donnees, data = "RP_LOGEMENT")
    def dont_find_match(self):
        self.assertRaises(ValueError, millesimesDisponibles, data = "randomword")
    def find_millesime_match(def):
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = "dernier"), dict)
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = "2012"), dict)
        self.assertIsInstance(info_donnees("RP_LOGEMENT", date = 2012), dict)
        self.assertIsInstance(info_donnees("SIRENE_SIRET_NONDIFF"), dict)


#chargerDonnees(telechargerFichier("ESTEL_T201_ENS_TBE", "dernier"))
#chargerDonnees(telechargerFichier("RP_LOGEMENT", "dernier"))

