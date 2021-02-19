# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 10:19:26 2021

@author: XLAPDO
"""

def _hash(string):
    import hashlib
    h = hashlib.new('ripemd160')
    h.update(string.encode('utf-8'))
    return(h.hexdigest())