# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pathlib2 import Path
import os
import yaml

def _get_credentials():

    # try to find insee keys in 'pynsee_api_credentials.py' located in HOME
    
    # try:
    #     home = str(Path.home())
    #     if os.path.exists(home):
    #         list_files = os.listdir(home)
    #         if 'pynsee_api_credentials.py' in list_files:        
    #             parameter_file = home + '/' + 'pynsee_api_credentials.py'
    #             exec(open(parameter_file).read())
    # except:
    #     pass

    try:
        home = str(Path.home())
    
        pynsee_credentials_file = home + '/' + 'pynsee_credentials.yml'

        with open(pynsee_credentials_file, "r") as creds:
            secrets = yaml.safe_load(creds)
        
        os.environ['insee_key'] = secrets["credentials"]["insee_key"]
        os.environ['insee_secret'] = secrets["credentials"]["insee_secret"]
        os.environ['http_proxy'] = secrets["credentials"]["proxy_server"]
        os.environ['https_proxy'] = secrets["credentials"]["proxy_server"]
    except:
        pass

    try:
        key_dict = {'insee_key': os.environ['insee_key'],
                    'insee_secret': os.environ['insee_secret']}
    except:
        key_dict = None

    return(key_dict)
