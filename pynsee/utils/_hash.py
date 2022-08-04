# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import hashlib


def _hash(string):

    h = hashlib.new("md5")
    h.update(string.encode("utf-8"))
    return h.hexdigest()
