# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 23:38:13 2021

@author: eurhope
"""

def get_local():
    
    from pynsee.utils._request_insee import _request_insee
    
    croisement = ''
    dataset = ''
    codgeo = ''
    nivgeo = ''
    
    link = 'https ://api.insee.fr/donnees-locales/V0.1/donnees/'
    link = link + 'geo-{}@{}/{}-{}.all'.format(croisement, dataset, nivgeo, codgeo)
    
    request = _request_insee(api_url = link)
    
    