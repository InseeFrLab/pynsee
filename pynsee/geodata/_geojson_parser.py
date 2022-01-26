# -*- coding: utf-8 -*-

#from tqdm import trange
import pandas as pd
from shapely.geometry import shape

def _geojson_parser(data):
        
    data_list = []
    
    for c in range(len(data)): 
           
        df = data[c]['properties']
        
        df2 = pd.DataFrame({f : df[f] for f in df.keys()\
                            if f not in (['geometry', 'bbox']) and
                            (type(df[f]) is not list)}, index=[0])
        
        for k in df.keys():
            dfk = df[k]
            if type(dfk) is list:
                try:
                    df2[k] = [df[k]]
                except:
                    pass        
        
        
        geom = data[c]['geometry']['coordinates']
        
        data_type = data[c]['geometry']['type']
        
        Shape = shape({"type": data_type,
                            "coordinates": geom})

        if data_type in ['LineString', 'Polygon', 'Point']:
            df2['geometry'] = Shape
        elif data_type in ['MultiLineString','MultiPolygon', 'MultiPoint']:
            df2['geometry'] = [Shape]
        else:
            geo_Shape = Shape.geoms
            if (len(geo_Shape) > 1):
                df2['geometry'] = [Shape]
            else:
                df2['geometry'] = Shape
                
        data_list.append(df2)
                
    data_all = pd.concat(data_list).reset_index(drop=True)
    
    return data_all
         