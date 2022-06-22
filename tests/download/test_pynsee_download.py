import unittest
import os
import pandas as pd

from pynsee.download import *
from pynsee.download import download_file
from pynsee.download import get_file_list
from pynsee.download import get_column_metadata
from pynsee.utils.clear_all_cache import clear_all_cache

class MyTests(unittest.TestCase):
    
    def test_get_file_list_error(self):
        
        os.environ["pynsee_file_list"] = "https://raw.githubusercontent.com/" + \
            "InseeFrLab/DoReMIFaSol/master/data-raw/test.json"
        
        clear_all_cache()        
        df = get_file_list()        
        clear_all_cache()
        
        self.assertTrue(isinstance(df, pd.DataFrame))
        
        
    def test_download_file_all(self):
        meta = get_file_list()
        self.assertTrue(isinstance(meta, pd.DataFrame))
        
        meta['size'] = pd.to_numeric(meta['size'])
        meta = meta[meta['size'] < 300000000].reset_index(drop=True)        
        
        list_file = list(meta.id)        
        list_file_check = list_file[:20] + list_file[-20:]
        list_file_check = ["COG_COMMUNE_2018", "AIRE_URBAINE", "FILOSOFI_COM_2015", "DECES_2020",
                   "PRENOM_NAT", "ESTEL_T201_ENS_T", "FILOSOFI_DISP_IRIS_2017",
                   "BPE_ENS", "RP_MOBSCO_2016"]
        
        for i, f in enumerate(list_file_check):
            print(f"{i} : {f}")

            df = download_file(f)
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
            
            df = download_file(list_file_check[0])
            self.assertTrue(isinstance(df, pd.DataFrame))
            
            
            
if __name__ == '__main__':
    unittest.main()

"""
import unittest

class KnownGood(unittest.TestCase):
    def __init__(self, input):
        super(KnownGood, self).__init__()
        self.input = input
    def runTest(self):
        self.assertEqual(type(download_file(self.input)), pd.DataFrame)

def suite():
    suite = unittest.TestSuite()
    list_file = ["COG_COMMUNE_2018", "AIRE_URBAINE", "FILOSOFI_COM_2015", "DECES_2020",
                   "PRENOM_NAT", "ESTEL_T201_ENS_T", "FILOSOFI_DISP_IRIS_2017",
                   "BPE_ENS", "RP_MOBSCO_2016"]
    suite.addTests(KnownGood(input) for input in list_file)
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
"""