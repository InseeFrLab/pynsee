
import os
import tqdm
import math
from shapely.affinity import translate as trs
from shapely.geometry import Point
import pandas as pd
import warnings

from pynsee.geodata._make_offshore_points import _make_offshore_points
from pynsee.geodata._rescale_geom import _rescale_geom
from pynsee.geodata._get_center import _get_center

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def translate(self, 
            departement = ['971', '972', '974', '973', '976'], 
            factors = [None, None, None, 0.35, None],
            center = (-133583.39, 5971815.98),
            radius = 650000,
            angle = 1/9*math.pi,
            startAngle = math.pi * (1 - 1.5 * 1/9)):
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    
        df = self

        crs = df.crs.unique()

        if crs != 'EPSG:3857':
            raise ValueError('!!! Translation is performed only if the crs is EPSG:3857 !!!')

        if 'insee_dep' in df.columns:

            offshore_points = _make_offshore_points(center = Point(center),
                                list_ovdep=departement,
                                radius = radius,
                                angle = angle,
                                startAngle = startAngle)

            list_new_dep = []      

            for d in range(len(departement)):

                ovdep = df[df['insee_dep'].isin([departement[d]])]

                if len(ovdep.index) > 0:

                    ovdep = ovdep.reset_index(drop=True)

                    if factors[d] is not None:
                        ovdep = _rescale_geom(ovdep, factor=factors[d])

                    center_x, center_y = _get_center(ovdep)

                    xoff = offshore_points[d].coords.xy[0][0] - center_x 
                    yoff = offshore_points[d].coords.xy[1][0] - center_y   

                    ovdep['geometry'] = ovdep['geometry'].apply(lambda x: trs(x, xoff=xoff, yoff=yoff))      

                    list_new_dep += [ovdep]

                else:
                    print(f"!!! {departement[d]} is missing from insee_dep column !!!")

            if len(list_new_dep) > 0 :

                ovdepGeo = pd.concat(list_new_dep) 

                mainGeo = df[~df['insee_dep'].isin(departement)].reset_index(drop=True)     

                finalDF = pd.concat([ovdepGeo, mainGeo]).reset_index(drop=True)

                self = finalDF
        else:
            raise ValueError('insee_dep is missing in columns')
    
    return self
