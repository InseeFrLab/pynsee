
import tqdm
import math
import multiprocessing
from shapely.affinity import translate
from shapely.geometry import Point
import pandas as pd

from pynsee.geodata._convert_polygon import _convert_polygon
from pynsee.geodata._convert_polygon import _convert_polygon_list
from pynsee.geodata._convert_polygon import _set_global_translate_overseas
from pynsee.geodata._make_offshore_points import _make_offshore_points
from pynsee.geodata._rescale_geom import _rescale_geom
from pynsee.geodata._get_center import _get_center

def translate_overseas(self, 
                        overseas = ['971', '972', '973', '974', '976'], 
                        factors = [None, None, None, 0.35, None],
                        center = (-1.2, 47.181903), 
                        length = 6,
                        pishare = 1/10):
    
    df = self
    
    if 'insee_dep' in df.columns:
        
        offshore_points = _make_offshore_points(center = Point(center), length = length, pishare = pishare)
            
        list_new_dep = []      
    
        for d in range(len(overseas)):
    
            ovdep = df[df['insee_dep'].isin([overseas[d]])]
    
            if len(ovdep.index) > 0:
    
                ovdep = ovdep.reset_index(drop=True)
                ovdep_geo = ovdep.get_geom()
    
                geo_3857 = _convert_polygon(ovdep_geo)
    
                if factors[d] is not None:
                    geo_3857 = _rescale_geom(geo_3857, factor=1-math.sqrt(factors[d]))
    
                center_x, center_y = _get_center(geo_3857)
    
                xoff = offshore_points[d].coords.xy[0][0] - center_x 
                yoff = offshore_points[d].coords.xy[1][0] - center_y         
    
                newgeo = translate(geo_3857, xoff=xoff, yoff=yoff)   
                ovdep["geometry"] = [newgeo] * len(ovdep.index)
    
                list_new_dep += [ovdep]
            
            else:
                print(f"!!! {overseas[d]} is missing from insee_dep column !!!")
        
        if len(list_new_dep) > 0 :
    
            mainGeo = df[~df['insee_dep'].isin(overseas)].reset_index(drop=True)       
            ovdepGeo = pd.concat(list_new_dep)
            
            
            Nprocesses = min(6, multiprocessing.cpu_count())
            
            list_geom = list(mainGeo["geometry"])
            args = [list_geom]
            irange = range(len(list_geom))        
                   
            with multiprocessing.Pool(initializer= _set_global_translate_overseas,
                                    initargs=(args,),
                                    processes=Nprocesses) as pool:
    
                list_geom_converted = list(tqdm.tqdm(pool.imap(_convert_polygon_list, irange),
                                        total=len(list_geom)))
                            
            mainGeo["geometry"] = list_geom_converted
            
            finalDF = pd.concat([ovdepGeo, mainGeo])
            finalDF["crs"] = 'EPSG:3857'
            
            self = finalDF
    else:
        print('insee_dep is missing in columns')
    
    return self
