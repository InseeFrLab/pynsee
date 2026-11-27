# -*- coding: utf-8 -*-
# Copyright : INSEE, 2026

import unittest
from unittest import TestCase
import pandas as pd

from pynsee.melodi import *

class test_pynsee_melodi(unittest.TestCase):

    def test_get_local_data_by_com(self):
        #Test standard
        df_com1 = get_local_data_by_com(
            ds_name="DS_POPULATIONS_REFERENCE", 
            geo="69", 
            geo_object="DEP"
        )
        self.assertIsInstance(
            df_com1, 
            pd.DataFrame, 
            "Problème format de sortie : ce n'est pas un dataframe."
        )
        self.assertGreater(df_com1.shape[0], 0, "Problème, le dataframe local par com 1 a 0 ligne.")
        self.assertGreater(df_com1.shape[1], 0, "Problème, le dataframe local par com 1 a 0 colonne.")

        #Test avec filtre additionnel
        df_com2 = get_local_data_by_com(
            ds_name="DS_POPULATIONS_REFERENCE", 
            geo="69", 
            geo_object="DEP", 
            query_filter="POPREF_MEASURE=PMUN"
        )
        self.assertIsInstance(
            df_com2, 
            pd.DataFrame, 
            "Problème format de sortie : ce n'est pas un dataframe."
        )
        self.assertGreater(df_com2.shape[0], 0, "Problème, le dataframe local par com 2 a 0 ligne.")
        self.assertGreater(df_com2.shape[1], 0, "Problème, le dataframe local par com 2 a 0 colonne.")

    def test_get_local_data(self):
        #Test standard avec géographie
        df_local1 = get_local_data(
            ds_name="DS_POPULATIONS_REFERENCE", 
            geo="69", 
            geo_object="DEP"
        )
        self.assertIsInstance(
            df_local1, 
            pd.DataFrame, 
            "Problème format de sortie : ce n'est pas un dataframe."
        )
        self.assertGreater(df_local1.shape[0], 0, "Problème, le dataframe local 1 a 0 ligne.")
        self.assertGreater(df_local1.shape[1], 0, "Problème, le dataframe local 1 a 0 colonne.")

        #Test avec filtre additionnel
        df_local2 = get_local_data(
            ds_name="DS_POPULATIONS_REFERENCE", 
            geo="69", 
            geo_object="DEP", 
            query_filter="POPREF_MEASURE=PMUN"
        )
        self.assertIsInstance(
            df_local2, 
            pd.DataFrame, 
            "Problème format de sortie : ce n'est pas un dataframe."
        )
        self.assertGreater(df_local2.shape[0], 0, "Problème, le dataframe local 2 a 0 ligne.")
        self.assertGreater(df_local2.shape[1], 0, "Problème, le dataframe local 2 a 0 colonne.")

    def test_get_range(self):
        df_fr = get_range("DS_EC_DECES")
        df_en = get_range("DS_EC_DECES", lang="en")
        
        #Vérification des types
        self.assertIsInstance(df_fr, pd.DataFrame, "Problème format de sortie : ce n'est pas un dataframe.")
        self.assertIsInstance(df_en, pd.DataFrame, "Problème format de sortie : ce n'est pas un dataframe.")
        
        #Vérification des dimensions
        self.assertGreater(df_fr.shape[0], 0, "Problème, le dataframe a 0 ligne.")
        self.assertGreater(df_fr.shape[1], 0, "Problème, le dataframe a 0 colonne.")
        
        #Vérification des colonnes attendues
        expected_columns = {"DIM", "DIM_LABEL", "MOD", "MOD_LABEL"}
        self.assertTrue(
            expected_columns.issubset(df_fr.columns), 
            f"Problème, les colonnes attendues {expected_columns} ne sont pas toutes présentes dans le dataframe."
        )

    def test_get_range_geo(self):
        df_ref = get_range_geo("DS_POPULATIONS_REFERENCE")
        df_ref_en = get_range_geo("DS_POPULATIONS_REFERENCE", lang="en")
        df_deces = get_range_geo("DS_EC_DECES")
        
        #Vérification des types
        self.assertIsInstance(df_ref, pd.DataFrame, "Problème format de sortie : ce n'est pas un dataframe.")
        self.assertIsInstance(df_ref_en, pd.DataFrame, "Problème format de sortie : ce n'est pas un dataframe.")
        
        #Vérification des dimensions
        self.assertGreater(df_ref.shape[0], 0, "Problème, le dataframe a 0 ligne.")
        self.assertGreater(df_ref.shape[1], 0, "Problème, le dataframe a 0 colonne.")
        
        #Vérification des colonnes attendues
        expected_columns = {"GEO_REF", "GEO_OBJECT", "GEO_OBJECT_LABEL", "GEO", "GEO_LABEL"}
        self.assertTrue(
            expected_columns.issubset(df_deces.columns), 
            f"Problème, les colonnes attendues {expected_columns} ne sont pas toutes présentes dans le dataframe."
        )

    def test_get_metadata(self):
        #Vérification du type de retour (en appelant la fonction une seule fois)
        try:
            metadata = get_metadata("DS_POPULATIONS_REFERENCE")
        except Exception as e:
            self.fail(f"Erreur lors de l'appel à get_metadata : {e}")
            
        #Vérification que le résultat est bien un dictionnaire
        self.assertIsInstance(
            metadata, 
            dict, 
            "Problème format de sortie : ce n'est pas un dictionnaire."
        )

    def test_get_file(self):
        #Téléchargement d'un fichier Excel
        get_file(
            ds_name="DS_EC_DECES",
            file_name="T1_DECES_JOUR_NAT_FR",
            download_file_name="T1_DECES_JOUR_NAT_FR.xlsx",
        )

        #Téléchargement d'un fichier CSV / ZIP
        get_file(
            ds_name="DS_EC_DECES",
            file_name="DS_EC_DECES_CSV_FR",
            download_file_name="DS_EC_DECES_CSV_FR.zip",
        )

        #Téléchargement d'un fichier Parquet
        get_file(ds_name="DS_BTS_SAL_EQTP_SEX_PCS")

    def test_get_data(self):
        #Test DS sans attribut
        url_no_attr = "https://api.insee.fr/melodi/data/DS_POPULATIONS_REFERENCE?POPREF_MEASURE=PMUN&GEO=FRANCE-F"
        df_no_attr = get_data(url_no_attr)
        self.assertIsInstance(
            df_no_attr, pd.DataFrame, "DS sans attribut, problème format de sortie : ce n'est pas un DataFrame."
        )
        self.assertGreater(df_no_attr.shape[0], 0, "DS sans attribut : le DataFrame a 0 ligne.")
        self.assertGreater(df_no_attr.shape[1], 0, "DS sans attribut : le DataFrame a 0 colonne.")

        #Test DS avec attribut
        url_attr = "https://api.insee.fr/melodi/data/DS_EC_DECES?SEX=_T&GEO=FRANCE"
        df_attr = get_data(url_attr)
        self.assertIsInstance(
            df_attr, pd.DataFrame, "DS avec attribut, problème format de sortie : ce n'est pas un DataFrame."
        )
        self.assertGreater(df_attr.shape[0], 0, "DS avec attribut : le DataFrame a 0 ligne.")
        self.assertGreater(df_attr.shape[1], 0, "DS avec attribut : le DataFrame a 0 colonne.")

        #Test de la limite des 10 000 lignes (avec regex sur le message d'erreur)
        with self.assertRaisesRegex(ValueError, r"^Request over 100,000 lines not supported yet,\nplease filter your request or use get_all_data$"):
            get_data("https://api.insee.fr/melodi/data/DS_EC_DECES?GEO=DEP")

        #Test d'une autre erreur ValueError sur les paramètres
        with self.assertRaises(ValueError):
            get_data("https://api.insee.fr/melodi/data/DS_EC_DECES?SEX=_T&AGE=_T&DTH_PLACE=1&FREQ=A&GEO=FRANCE")


    def test_get_catalog(self):
    
        #Test de la gestion d'erreur sur un paramètre de langue invalide
        with self.assertRaises(ValueError) as test_message_erreur:
            get_catalog(lang="français")
        self.assertIn(
        "lang must be 'fr' or 'en'", str(test_message_erreur.exception)
        )

        #Test de la version anglaise
        catalog_en = get_catalog(lang="en")
        self.assertIsInstance(
            catalog_en, pd.DataFrame, "Problème avec la version anglaise : ce n'est pas un DataFrame."
        )
        self.assertGreater(catalog_en.shape[0], 0, "Problème avec la version anglaise : le DataFrame a 0 ligne.")
        self.assertGreater(catalog_en.shape[1], 0, "Problème avec la version anglaise : le DataFrame a 0 colonne.")

        #Test de la version française
        catalog_fr = get_catalog(lang="fr")
        self.assertIsInstance(
            catalog_fr, pd.DataFrame, "Problème avec la version française : ce n'est pas un DataFrame."
        )
        self.assertGreater(catalog_fr.shape[0], 0, "Problème avec la version française : le DataFrame a 0 ligne.")
        self.assertGreater(catalog_fr.shape[1], 0, "Problème avec la version française : le DataFrame a 0 colonne.")
  
    def test_get_all_data(self):
        # Appel unique pour récupérer les données et les métadonnées
        data, metadata = get_all_data("DS_TICM_PRATIQUES", remove_file=False)

        # Vérifications sur le DataFrame des données (index 0)
        self.assertIsInstance(
            data, pd.DataFrame, "Ce n'est pas un DataFrame pour les données."
        )
        self.assertGreater(data.shape[0], 0, "Problème, le DataFrame a 0 ligne.")
        self.assertGreater(data.shape[1], 0, "Problème, le DataFrame a 0 colonne.")

        # Vérifications sur le DataFrame des métadonnées (index 1)
        self.assertIsInstance(
            metadata, pd.DataFrame, "Ce n'est pas un DataFrame pour les métadonnées."
        )
        self.assertGreater(metadata.shape[0], 0, "Problème, le DataFrame a 0 ligne.")
        self.assertGreater(metadata.shape[1], 0, "Problème, le DataFrame a 0 colonne.")

if __name__ == '__main__':
  
#Création d'un lanceur de tests (Test Runner) textuel
    runner = unittest.TextTestRunner()

#Chargement des tests de la classe et exécution.
#Le stockage dans 'result' permet d'analyser le compte-rendu juste après.
    result = runner.run(
      unittest.defaultTestLoader.loadTestsFromTestCase(test_pynsee_melodi))

#Vérification du succès global et affichage d'un message personnalisé
    if result.wasSuccessful():
        print(
        "\n✨ Félicitations ! Tous les tests du sous-module melodi sont OK !")
    else:
        print("\n❌ Attention, certains tests ont échoué.")
