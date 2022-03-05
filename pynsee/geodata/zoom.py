import pandas as pd
import math
from shapely.affinity import translate as trs
from shapely.affinity import rotate
from shapely.geometry import Point, LineString

from pynsee.geodata._extract_bounds import _extract_bounds
from pynsee.geodata._rescale_geom import _rescale_geom
from pynsee.geodata._get_center import _get_center

def zoom(self, 
        departement = ['75','92', '93','94'], #'91', '78', '77', '95'
        center = (-133583.39, 5971815.98),
        radius = 650000,
        angle = math.pi * (1 - 3.5 * 1/9),
        factor = 2):

    df = self

    if all([x in df.columns for x in ['insee_dep', 'geometry']]):
        
        zoomDeps = df[df['insee_dep'].isin(departement)]        
        zoomDeps = zoomDeps.reset_index(drop=True)
        zoomDepsGeo = zoomDeps.get_geom()
        centerZoom = _get_center(zoomDepsGeo)
        
        list_dep_scaled = []
        
        for d in departement:
            zoomDep = df[df['insee_dep'] == d].reset_index(drop=True)
        
            zoomDepGeo = zoomDep.get_geom()
            zoomDepGeo = _rescale_geom(geo = zoomDepGeo, factor = factor, center=centerZoom)
            
            end = Point(center[0] + radius, center[1])
            line = LineString([center, end])
            line = rotate(line, angle, origin=center, use_radians=True)
            endPoint = Point(line.coords[1])
                    
            maxxdep = max(_extract_bounds(zoomedDepGeo, var= 'maxx'))
            maxydep = max(_extract_bounds(zoomedDepGeo, var= 'maxy'))
            
            xoff = endPoint.coords.xy[0][0] - maxxdep 
            yoff = endPoint.coords.xy[1][0] - maxydep 
        
        #zoomedDep['geometry'] = zoomedDep['geometry'].apply(lambda x: trs(x, xoff=xoff, yoff=yoff))

        self = pd.concat([self, zoomedDep])                

    return self