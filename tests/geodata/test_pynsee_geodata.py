# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

from unittest import TestCase
import pandas as pd
import sys

from pynsee.geodata.get_geodata_list import get_geodata_list

class TestFunction(TestCase):

    def test_get_geodata_list(self):
        df = get_geodata_list()
        self.assertTrue(isinstance(df, pd.DataFrame))