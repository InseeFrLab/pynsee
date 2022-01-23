# -*- coding: utf-8 -*-

import requests
import tempfile

from functools import lru_cache

@lru_cache(maxsize=None)
def _get_capabilities(key, version='1.0.0', service='wmts', tweak =''):
    
    service_upper = service.upper()
    
    link = 'https://wxs.ign.fr/{}/geoportail/{}{}?SERVICE={}&VERSION={}&REQUEST=GetCapabilities'.format(key, tweak, service, service_upper, version)
        
    results = requests.get(link)
    
    raw_data_file = tempfile.mkdtemp() + '\\' + "raw_data_file"

    with open(raw_data_file, 'wb') as f:
        f.write(results.content)
        f.close()
        
    return(raw_data_file)