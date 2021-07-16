# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import yaml
from pathlib2 import Path

def init_conn(insee_key, insee_secret, proxy_server=""):
    """Save your credentials to connect to INSEE APIs

    Args:
        insee_key (str): [description]
        insee_secret (str): [description]
        proxy_server (str, optional): [description]. Defaults to "".

    Examples:
        >>> from pynsee.utils.init_conn import init_conn
        >>> init_conn(insee_key="my_insee_key", insee_secret="my_insee_secret")
    """    
    d = {'credentials':{'insee_key': insee_key,
                  'insee_secret': insee_secret,
                  'proxy_server': proxy_server}}
    
    home = str(Path.home())
    
    pynsee_credentials_file = home + '/' + 'pynsee_credentials.yml'
    
    with open(pynsee_credentials_file, 'w') as yaml_file:
        yaml.dump(d, yaml_file, default_flow_style=False)
        yaml_file.close()
        