# -*- coding: utf-8 -*-

from pynsee.local import *

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import descartes

# get a list all data available : datasets and variables
metadata = get_local_metadata()

# geographic metadata
nivgeo = get_nivgeo_list()

# get geographic area list
area = get_area_list()

# get all communes in Paris urban area
areaParis = get_insee_area('unitesUrbaines2020', ['00851'])

# get selected communes identifiers
code_com_paris = areaParis.code.to_list()

# get numeric values from INSEE database 
dataParis = get_insee_local(dataset='GEO2020FILO2017',
                       variables =  'INDICS_FILO_DISP_DET',
                       geo = 'COM',
                       geocodes = code_com_paris)

#select poverty rate data
data_plot = dataParis.loc[dataParis.UNIT=='TP60']

#get communes limits
map = get_map('communes')

# merge values and geographic limits
mapparis = map.merge(data_plot, how = 'right',
                     left_on = 'code', right_on = 'CODEGEO')

#plot
fig, ax = plt.subplots(1,1,figsize=[15,15])
mapparis.plot(column='OBS_VALUE', cmap=cm.viridis, 
    legend=True, ax=ax, legend_kwds={'shrink': 0.3})
ax.set_axis_off()
ax.set(title='Poverty rate in Paris urban area in 2017')
plt.show()
fig.savefig('poverty_paris_urban_area.png')












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