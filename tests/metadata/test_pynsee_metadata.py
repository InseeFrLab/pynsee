# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from unittest import TestCase
from pandas import pandas as pd

from pynsee.metadata.get_definition_list import get_definition_list
from pynsee.metadata.get_definition import get_definition
from pynsee.metadata.get_activity_list import get_activity_list


class TestFunction(TestCase):

    if False:

        def test_get_definition_list(self):
            data = get_definition_list()
            self.assertTrue(isinstance(data, pd.DataFrame))

        def test_get_definition(self):
            data = get_definition(ids=['c1020', 'c1601'])
            self.assertTrue(isinstance(data, pd.DataFrame))

        def test_get_activity_list(self):
            test = True
            level_available = ['A10', 'A21', 'A38', 'A64', 'A88', 'A129', 'A138',
                            'NAF1', 'NAF2', 'NAF3', 'NAF4', 'NAF5']
            for nomencl in level_available:
                data = get_activity_list(nomencl)
                test = test & isinstance(data, pd.DataFrame)
            self.assertTrue(test)
