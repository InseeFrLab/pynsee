# -*- coding: utf-8 -*-

from pynsee.local.get_local_metadata import get_local_metadata
from pynsee.local.get_insee_local import get_insee_local
from pynsee.local.get_nivgeo_list import get_nivgeo_list
from pynsee.local.get_geo_list import get_geo_list
from pynsee.local.get_area_list import get_area_list
from pynsee.local._get_geo_list_simple import _get_geo_list_simple
from pynsee.local.get_map import get_map

from pynsee.local import *

metadata = get_local_metadata()

meta = metadata.loc[metadata.variables.str.contains('SEXE')]

nivgeo = get_nivgeo_list()

area = get_area_list()

reg = get_geo_list('regions')
dep = get_geo_list('departements')
coma = get_geo_list('communesAssociees')


com = get_geo_list('communes')
com_dep = com.loc[com.CODE_DEP=='91']
code_dep_list = com_dep.CODE.to_list()

data = get_insee_local(dataset='GEO2020FILO2017',
                       variables =  'INDICS_FILO_DISP_DET',
                       geo = 'COM',
                       geocodes = code_dep_list)

data_plot = data.loc[data.UNIT=='D9']
map = get_map('communes')
map91 = map.merge(data_plot, how = 'right', left_on = 'code', right_on = 'CODEGEO')

map91.plot(column='OBS_VALUE')

#example2
import pandas as pd

map_list = get_map_list()

com = get_geo_list('communes')
com_paris = com.loc[com.CODE_DEP.isin(['92', '93', '94', '75']) ]
code_com_paris = com_paris.CODE.to_list()


dataParis = get_insee_local(dataset='GEO2020FILO2017',
                       variables =  'INDICS_FILO_DISP_DET',
                       geo = 'COM',
                       geocodes = code_com_paris)

data_plot = dataParis.loc[dataParis.UNIT=='TP60']
map = get_map('communes')
mapparis = map.merge(data_plot, how = 'right', left_on = 'code', right_on = 'CODEGEO')

mapparis.plot(column='OBS_VALUE')


arr = get_geo_list('arrondissementsMunicipaux')
arrParis = arr.loc[arr.CODE_DEP == '75']
code_arrParis = arrParis.CODE.to_list()

dataParisM = get_insee_local(dataset='GEO2020FILO2017',
                       variables =  'INDICS_FILO_DISP_DET',
                       geo = 'COM',
                       geocodes = code_arrParis)

dataP = pd.concat([dataParis, dataParisM])
dataP = dataP.loc[dataP.CODEGEO!='75056']

data_plot = dataP.loc[dataParis.UNIT=='TP60']


map = get_map('communes')
map_paris = map.merge(data_plot, how = 'right',
                      left_on = 'code', right_on = 'CODEGEO')


map_paris.plot(column='OBS_VALUE')




#ALL IDF
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import descartes

area_all = get_area_list('unitesUrbaines2020')

areaParis = get_insee_area('unitesUrbaines2020', ['00851'])

code_com_paris = areaParis.code.to_list()

#get data 
dataParis = get_insee_local(dataset='GEO2020FILO2017',
                       variables =  'INDICS_FILO_DISP_DET',
                       geo = 'COM',
                       geocodes = code_com_paris)

#select poverty rate data
data_plot = dataParis.loc[dataParis.UNIT=='TP60']

#get communes limits
map = get_map('communes')

# merge values and geographic limits
mapparis = map.merge(data_plot, how = 'right', left_on = 'code', right_on = 'CODEGEO')

#plot
fig, ax = plt.subplots(1,1,figsize=[10,10])
mapparis.plot(column='OBS_VALUE', cmap=cm.viridis, 
    legend=True, ax=ax, legend_kwds={'shrink': 0.3})
ax.set_axis_off()
ax.set(title='Poverty rate in Paris urban area in 2017')
plt.show()













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