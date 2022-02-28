# -*- coding: utf-8 -*-

#from tqdm import trange
import pandas as pd
from shapely.geometry import shape
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, MultiLineString, MultiPoint
import warnings

def _geojson_parser(data):
        
    data_list = []
    list_shapes = []

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
        
        Shape = shape({"type": data_type, "coordinates": geom})
        # list_shapes = [Shape.geoms[x] for x in range(len(Shape.geoms))]

        if data_type in ['MultiLineString','MultiPolygon', 'MultiPoint','LineString', 'Polygon', 'Point']:
            list_shapes += [Shape]
            data_list.append(df2)
        else:            
            print(f"Unsupported shape {data_type} has been removed")
                    

    data_all = pd.concat(data_list)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data_all["geometry"] = list_shapes

    return data_all
         