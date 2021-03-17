
def _get_nivgeo():
    import pandas as pd
    dict_ng = {
            'nivgeo':['COM',
                      'DEP',
                      'REG',
                      'METRODOM',
                      'FE',
                      'ARR',
                      'EPCI',
                      'AAV2020',
                      'UU2020',
                      'ZE2020',
                      'AU2010',
                      'UU2010',
                      'ZE2010'],
            'nivgeo_label_fr':['communes et arrondissements municipaux',
                               'départements',
                               'régions',
                               'France métropolitaine',
                               'France',
                               'arrondissements',
                               'intercommunalités',
                               "aires d'attraction des villes 2020",
                               'unités urbaines 2020',
                               "zones d'emploi 2020",
                               "aires urbaines 2010",
                               'unités urbaines 2010',
                               "zones d'emploi 2010"]}
            
    nivgeo= pd.DataFrame(dict_ng)
    return(nivgeo)