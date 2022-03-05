import pandas as pd
import math
from shapely.affinity import translate as trs
from shapely.affinity import rotate
from shapely.geometry import Point, LineString

from pynsee.geodata._extract_bounds import _extract_bounds
from pynsee.geodata._rescale_geom import _rescale_geom

def zoom(self, 
        departement = ['75','92', '93','94'], #'91', '78', '77', '95'
        center = (-133583.39, 5971815.98),
        radius = 650000,
        angle = math.pi * (1 - 3.5 * 1/9),
        factor = 0.1):

    df = self

    if all([x in df.columns for x in ['insee_dep', 'geometry']]):
        
        zoomedDep = df[df['insee_dep'].isin(departement)]        
        zoomedDep = zoomedDep.reset_index(drop=True)
        zoomedDepGeo = zoomedDep.get_geom()
        
        zoomedDepGeo = _rescale_geom(geo = zoomedDepGeo, factor = factor)
        
        end = Point(center[0] + radius , center[1] )
        line = LineString([center, end])
        line = rotate(line, angle, origin=center, use_radians=True)
        endPoint = Point(line.coords[1])
                
        maxxdep = max(_extract_bounds(zoomedDepGeo, var= 'maxx'))
        maxydep = max(_extract_bounds(zoomedDepGeo, var= 'maxy'))
        
        xoff = endPoint.coords.xy[0][0] - maxxdep 
        yoff = endPoint.coords.xy[1][0] - maxydep 
        zoomedDep['geometry'] = zoomedDep['geometry'].apply(lambda x: trs(x, xoff=xoff, yoff=yoff))

        self = pd.concat([self, zoomedDep])                

    return self