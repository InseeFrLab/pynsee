# -*- coding: utf-8 -*-

from functools import lru_cache

@lru_cache(maxsize=None)
def get_geo_list(geo):    
    """Get a list of French geographic areas (communes, departements, regions ...)

    Args:
        geo (str): choose among : 'communes', 'regions', 'departements',
                          'arrondissements', 'arrondissementsMunicipaux'

    Raises:
        ValueError: geo should be among the geographic area list
    
    Examples:
    ---------
    >>> city_list = get_geo_list('communes')
    >>> region_list = get_geo_list('regions')
    >>> departement_list = get_geo_list('departements')
    """   
    import pandas as pd
    from tqdm import trange
    
    from pynsee.utils._paste import _paste
    from pynsee.local._get_geo_relation import _get_geo_relation
    from pynsee.local._get_geo_list_simple import _get_geo_list_simple
    
    list_available_geo = ['communes', 'communesDeleguees', 'communesAssociees',
                          'regions', 'departements',
                          'arrondissements', 'arrondissementsMunicipaux']
    geo_string = _paste(list_available_geo, collapse = " ")
    
    if not geo in list_available_geo:
        msg = "!!! {} is not available\nPlease choose geo among:\n{}".format(geo, geo_string)
        raise ValueError(msg)
        
    reg = _get_geo_list_simple('regions', progress_bar=True)
    reg.columns = ['TITLE', 'TYPE', 'DATECREATION',
                          'TITLE_SHORT', 'CHEFLIEU', 'CODE', 'URI']
    
    if geo != 'regions':  
        list_reg = list(reg.CODE)
        list_data_reg = []
        
        for r in trange(len(list_reg), desc = 'Getting {}'.format(geo)):
            list_data_reg.append(_get_geo_relation('region', list_reg[r], 'descendants'))
            
        data_all = pd.concat(list_data_reg)
        data_all.columns = ['TITLE', 'TYPE', 'DATECREATION',
                            'TITLE_SHORT', 'CHEFLIEU', 'CODE', 'URI', 'geo_init']
        reg_short = reg[['TITLE', 'CODE']]
        reg_short.columns = ['TITLE_REG', 'CODE_REG']
        data_all = data_all.merge(reg_short, how = 'left', 
                                  left_on = 'geo_init', right_on = 'CODE_REG')
    
        if geo == 'communes':
            data_all = data_all.loc[data_all['TYPE'].str.match('^Commune$')]
        if geo == 'communesDeleguees':
            data_all = data_all.loc[data_all['TYPE'].str.match('^CommuneDeleguee$')]
        if geo == 'communesAssociees':
            data_all = data_all.loc[data_all['TYPE'].str.match('^CommuneAssociee$')]
        if geo == 'arrondissements':
            data_all = data_all.loc[data_all['TYPE'].str.match('^Arrondissement$')]
        if geo == 'arrondissementsMunicipaux':
            data_all = data_all.loc[data_all['TYPE'].str.match('^ArrondissementMunicipal$')]
        if geo == 'departements':
            data_all = data_all.loc[data_all['TYPE'].str.match('^Departement$')]
        
        data_all = data_all[['TITLE', 'TYPE', 'DATECREATION',
                               'TITLE_SHORT', 'CHEFLIEU', 'CODE', 'URI', 'CODE_REG', 'TITLE_REG']]
        
        if geo != 'departements':
            dep = _get_geo_list_simple('departements', progress_bar=True)
            dep.columns = ['TITLE', 'TYPE', 'DATECREATION',
                              'TITLE_SHORT', 'CHEFLIEU', 'CODE', 'URI']
            dep_short = dep[['CODE', 'TITLE']]
            dep_short.columns = ['CODE_dep', 'TITLE_DEP1']
            
            dep_short2 = dep[['CODE', 'TITLE']]
            dep_short2.columns = ['CODE_dep', 'TITLE_DEP2']
                        
            data_all = data_all.assign(code_dep1 = data_all['CODE'].str[:2],
                                       code_dep2 = data_all['CODE'].str[:3])
            
            data_all = data_all.merge(dep_short, how = 'left', left_on = 'code_dep1', right_on = 'CODE_dep')
            data_all = data_all.merge(dep_short2, how = 'left', left_on = 'code_dep2', right_on = 'CODE_dep')
            
            for i in range(len(data_all.index)):  
                if pd.isna(data_all.loc[i, 'TITLE_DEP1']):
                    data_all.loc[i, 'CODE_DEP'] = data_all.loc[i, 'code_dep2']
                    data_all.loc[i, 'TITLE_DEP'] = data_all.loc[i, 'TITLE_DEP2']
                else:
                    data_all.loc[i, 'CODE_DEP'] = data_all.loc[i, 'code_dep1']
                    data_all.loc[i, 'TITLE_DEP'] = data_all.loc[i, 'TITLE_DEP1']  
                
            
            data_all = data_all[['TITLE', 'TYPE', 'DATECREATION',
                                 'TITLE_SHORT', 'CHEFLIEU', 'CODE', 'URI',
                                 'CODE_REG', 'TITLE_REG', 'CODE_DEP', 'TITLE_DEP']]
        
        df_geo = data_all        
    else:
        df_geo = reg
    return(df_geo)
