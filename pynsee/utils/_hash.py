# -*- coding: utf-8 -*-
import hashlib

def _hash(string):
    
    h = hashlib.new('ripemd160')
    h.update(string.encode('utf-8'))
    return(h.hexdigest())