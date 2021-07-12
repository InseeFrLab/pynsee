import unittest

import pynsee.download.info_donnees as info_donnees
import pynsee.download.millesimesDisponibles as millesimesDisponibles

class MyTestCase(unittest.TestCase):
    def test_levensthein_error(self):
        self.assertRaises(ValueError, info_donnees, data = "SIRENE_SIRET_NONDIFg")
        self.assertRaises(ValueError, info_donnees, data = "randomword")
    def dont_find_match(self):
        self.assertRaises(ValueError, millesimesDisponibles, data = "randomword")
    def find_millesime_match(def):
        self.assertIsInstance(millesimesDisponibles("RP_LOGEMENT"), int)

