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
        
        try:
            geom = data[c]['geometry']['coordinates']
            
            data_type = data[c]['geometry']['type']
            
            multipolygon = shape({"type": data_type,
                                "coordinates": geom})
    
            if data_type in ['LineString', 'Polygon', 'Point']:
                df2['geometry'] = multipolygon
            elif data_type in ['MultiLineString','MultiPolygon', 'MultiPoint']:
                df2['geometry'] = [multipolygon]
            else:
                geo_multipoly = multipolygon.geoms
                if (len(geo_multipoly) > 1):
                    df2['geometry'] = [multipolygon]
                else:
                    df2['geometry'] = multipolygon
        except:
            print("!! No coordinates found for {} !!".format(c))
            pass        
        data_list.append(df2)
                
    data_all = pd.concat(data_list).reset_index(drop=True)
    
    return data_all
         