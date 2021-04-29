# -*- coding: utf-8 -*-

def _hash(string):
    import hashlib
    h = hashlib.new('ripemd160')
    h.update(string.encode('utf-8'))
    return(h.hexdigest())