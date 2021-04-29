# -*- coding: utf-8 -*-
import requests, re, os, base64

from functools import lru_cache

@lru_cache(maxsize=None)
def _get_token_from_insee():

    string_key = "{}:{}".format(os.environ['insee_key'], os.environ['insee_secret'])
    string_key_encoded = string_key.encode("utf-8")
    string = base64.b64encode(string_key_encoded).decode("utf-8")
    
    headers = {
        'Authorization': 'Basic {}'.format(string),
    }
    
    data = {
      'grant_type': 'client_credentials'
    }
    
    response = requests.post('https://api.insee.fr/token', headers=headers,
                             data=data, verify=True)
    
    content = response.content.decode("utf-8")
    content_splitted = content.split(",")
    list_access_token = [('access_token' in string) for string in content_splitted]
    selected_content =  [x for x, y in zip(content_splitted, list_access_token) if y]
    selected_content = selected_content[0]
    
    token = re.sub(':|"|}|{|access_token', "", selected_content)    

    return(token)




