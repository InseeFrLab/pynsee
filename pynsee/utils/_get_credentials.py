# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pathlib2 import Path
import os
import yaml

def _get_credentials():

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
        try:
            key_dict = {'insee_key': os.environ['INSEE_KEY'],
                        'insee_secret': os.environ['INSEE_SECRET']}
        except:
            key_dict = None

    return(key_dict)
