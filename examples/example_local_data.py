# -*- coding: utf-8 -*-

from pynsee.local.get_local_metadata import get_local_metadata
from pynsee.local.get_insee_local import get_insee_local
from pynsee.local.get_nivgeo_list import get_nivgeo_list
from pynsee.local.get_geo_list import get_geo_list
from pynsee.local.get_area_list import get_area_list
from pynsee.local._get_geo_list_simple import _get_geo_list_simple
from pynsee.local.get_map import get_map

metadata = get_local_metadata()

meta = metadata.loc[metadata.variables.str.contains('SEXE')]

nivgeo = get_nivgeo_list()

area = get_area_list()

reg = get_geo_list('regions')
dep = get_geo_list('departements')

coma = get_geo_list('communesAssociees')

com2 = _get_geo_list_simple('communes', progress_bar=True)

com = get_geo_list('communes')
com_dep = com.loc[com.CODE_DEP=='91']
code_com_list = com_dep.CODE.to_list()[1:40]
code_dep_list = dep.CODE.to_list()

data = get_insee_local(dataset='GEO2020RP2017',
                       variables =  'SEXE-DIPL_19',
                       geo = 'DEP',
                       geocodes = code_dep_list)

data = get_insee_local(dataset='GEO2020FILO2018',
                       variables =  'INDICS_FILO_DISP_DET-TRAGERF',
                       geo = 'REG',
                       geocodes = ['11', '01'])

data = get_insee_local(dataset='BDCOM2017',
                       variables =  'INDICS_BDCOM',
                       geo = 'REG',
                       geocodes = ['11'])

data = get_insee_local(dataset= 'GEO2019RFD2011',
                       variables = 'INDICS_ETATCIVIL',
                       geo = 'REG',
                       geocodes = ['11'])

data = get_insee_local(dataset= 'TOUR2019',
                       variables = 'ETOILE',
                       geo = 'REG',
                       geocodes = ['11'])

data = get_insee_local(dataset= 'GEO2020FLORES2017',
                       variables = 'EFFECSAL5T_1_100P',
                       geo = 'REG',
                       geocodes = ['11'])

data = get_insee_local(dataset= 'GEO2019REE2018',
                       variables = 'NA5_B',
                       geo = 'REG',
                       geocodes = ['11'])

data = get_insee_local(dataset= 'POPLEG2018',
                       variables = 'IND_POPLEGALES',
                       geo = 'COM',
                       geocodes = ['91477'])






data = get_insee_local(dataset='GEO2019RP2011',
                       variables =  'AGESCOL-SEXE-ETUD',
                       geo = 'DEP',
                       geocodes = ['91','92', '976'])

data = get_insee_local(dataset='RP2014',
                       variables =  'SEXE-DIPL_15',
                       geo = 'DEP',
                       geocodes = ['91','92', '976'])


map = get_map('communes')
map.plot(column='value')

    # test
    # import matplotlib
    # import descartes
    # map = get_map('communes')
    # map.plot(column='value')
    
#FAIL
#data = get_insee_local(dataset='GEO2020FILO2018',
#                       variables =  'INDICS_FILO_DISP_DET-TRAGERF',
#                       geo = 'DEP',
#                       geocodes = ['91','92', '976'])