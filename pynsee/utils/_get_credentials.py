# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pathlib2 import Path
import os

def _get_credentials():

    # try to find insee keys in 'pynsee_api_credentials.py' located in HOME
    
    try:
        home = str(Path.home())
        if os.path.exists(home):
            list_files = os.listdir(home)
            if 'pynsee_api_credentials.py' in list_files:        
                parameter_file = home + '/' + 'pynsee_api_credentials.py'
                exec(open(parameter_file).read())
    except:
        pass

    try:
        key_dict = {'insee_key': os.environ['insee_key'],
                    'insee_secret': os.environ['insee_secret']}
    except:
        key_dict = None

    return(key_dict)