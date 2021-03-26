# -*- coding: utf-8 -*-

def get_map_list():
    import pandas as pd
    maps_list = {
            'name_fr':['arrondissements',
                    'arrondissements-avec-outre-mer',
                    'arrondissements-version-simplifiee',
                    'arrondissements-municipaux',
                    'cantons',
                    'cantons-avec-outre-mer',
                    'cantons-version-simplifiee',
                    'communes',
                    'communes-avec-outre-mer',
                    'communes-version-simplifiee',
                    'departements',
                    'departements-avec-outre-mer',
                    'departements-version-simplifiee',
                    'metropole',
                    'metropole-et-outre-mer',
                    'metropole-version-simplifiee',
                    'regions',
                    'regions-avant-redecoupage-2015',
                    'regions-avec-outre-mer',
                    'regions-version-simplifiee'],
             'name_en':['arrondissements',
                    'arrondissements-with-overseas',
                    'arrondissements-version-simplified',
                    'arrondissements-municipaux',
                    'cantons',
                    'cantons-with-overseas',
                    'cantons-version-simplified',
                    'communes',
                    'communes-with-overseas',
                    'communes-version-simplified',
                    'departements',
                    'departements-with-overseas',
                    'departements-version-simplified',
                    'metropole',
                    'metropole-with-overseas',
                    'metropole-version-simplified',
                    'regions',
                    'regions-before-modification-2015',
                    'regions-with-overseas',
                    'regions-version-simplified']
            }
    maps_list = pd.DataFrame(maps_list)
    return(maps_list)