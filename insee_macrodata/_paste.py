# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 00:01:40 2020

@author: eurhope
"""

def _reduce_concat(x, sep=""):
    import functools
    return functools.reduce(lambda x, y: str(x) + sep + str(y), x)
 
def _paste(*lists, sep=" ", collapse=None):
    result = map(lambda x: _reduce_concat(x, sep=sep), zip(*lists))
    if collapse is not None:
          return _reduce_concat(result, sep=collapse)
          return list(result)