
import os
import tqdm
import math
from shapely.affinity import translate
from shapely.geometry import Point
import pandas as pd

from pynsee.geodata._convert_polygon import _convert_polygon
from pynsee.geodata._convert_main import _convert_main
from pynsee.geodata._make_offshore_points import _make_offshore_points
from pynsee.geodata._rescale_geom import _rescale_geom
from pynsee.geodata._get_center import _get_center

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def translate_overseas(self, 
                        overseas = ['971', '972', '973', '974', '976'], 
                        factors = [None, None, None, 0.35, None],
                        center = (-1.2, 47.181903), 
                        length = 6,
                        pishare = 1/10,
                        update=False):
    
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

            ovdepGeo = pd.concat(list_new_dep) 
    
            mainGeo = df[~df['insee_dep'].isin(overseas)].reset_index(drop=True)     
            
            ids = df['id'].to_list()

            filename = _hash("".join(ids + overseas))
            insee_folder = _create_insee_folder()
            file_geodata = insee_folder + "/" + filename

            if (not os.path.exists(file_geodata)) or update:            
                mainGeo = _convert_main(mainGeo=mainGeo, file_geodata=file_geodata)
            else:
                try:
                    mainGeo = pd.read_pickle(file_geodata)
                except:
                    os.remove(file_geodata)
                    mainGeo = _convert_main(mainGeo=mainGeo, file_geodata=file_geodata)
                else:
                    print(f'Locally saved data has been used\nSet update=True to trigger an update')
            
            finalDF = pd.concat([ovdepGeo, mainGeo])
            finalDF["crs"] = 'EPSG:3857'
            
            self = finalDF
    else:
        print('insee_dep is missing in columns')
    
    return self
