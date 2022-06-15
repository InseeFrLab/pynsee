import unittest
import warnings
import os.path
import hashlib
import pandas as pd

from pynsee.download import *
from pynsee.download import download_file
from pynsee.download import get_file_list

class MyTests(unittest.TestCase):
    
    def test_get_file_list(self):
        df = get_file_list()
        self.assertTrue(isinstance(df, pd.DataFrame))
    
    def test_download_file(self):
        meta = get_file_list()
        list_file = list(meta.id)        
        list_file_check = list_file[:100] + list_file[-100:]
        
        for i, f in enumerate(list_file_check):
            print(f"{i} : {f}")
            df = download_file(f)
        
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue((len(df.columns) > 2))
            
            
if __name__ == '__main__':
    unittest.main()


