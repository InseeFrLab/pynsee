import unittest
import warnings
import os.path
import hashlib
import pandas as pd

from pynsee.download import *
from pynsee.download import download_file
from pynsee.download import get_file_list
from pynsee.download import get_column_label

class MyTests(unittest.TestCase):
        
    def test_download_file_all(self):
        meta = get_file_list()
        self.assertTrue(isinstance(meta, pd.DataFrame))
        
        meta['size'] = pd.to_numeric(meta['size'])
        meta = meta[meta['size'] < 300000000].reset_index(drop=True)        
        
        list_file = list(meta.id)        
        list_file_check = list_file[:20] + list_file[-20:]
        list_file_check = ["COG_COMMUNE_2018", "AIRE_URBAINE", "FILOSOFI_COM_2015", "DECES_2020",
                           "PRENOM_NAT", "PRENOM_DEP", "ESTEL_T201_ENS_T", "ESTEL_T202_2016", "FILOSOFI_DISP_IRIS_2017",
                           "BPE_ENS", "RP_MOBSCO_2016", "RP_MOBZELT_2016"]
        
        for i, f in enumerate(list_file_check):
            print(f"{i} : {f}")
            df = download_file(f, metadata=True)
            label = get_column_label(id=f)
            
            if label is None:
                checkLabel = True
            elif isinstance(label, pd.DataFrame):
                checkLabel = True
            else: 
                checkLabel = False
                
            self.assertTrue(checkLabel)
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue((len(df.columns) > 2))
            
            
if __name__ == '__main__':
    unittest.main()


