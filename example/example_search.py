# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 17:30:28 2021

@author: XLAPDO
"""

from insee_macrodata import * 

search_all = search_insee()

search_paper = search_insee("pâte à papier")

search_paris = search_insee("PARIS")

search_survey_gdp = search_insee("Survey|GDP")
