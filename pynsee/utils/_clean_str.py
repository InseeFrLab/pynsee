# -*- coding: utf-8 -*-

import re

def _clean_str(string):
    return(re.sub('\{.*\}','', string))
