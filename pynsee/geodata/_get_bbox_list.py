# -*- coding: utf-8 -*-

import os
import numpy as np
import requests
import pickle
from shapely.geometry import Point, Polygon, MultiPolygon

from pynsee.geodata._geojson_parser import _geojson_parser

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash


def _get_bbox_list(polygon=None, update=False):
    
    try:
        name = '_get_bbox_list'
        
        if polygon is not None:
            name += ''.join([str(i) for i in list(polygon.bounds)])
                
        insee_folder = _create_insee_folder()
        file_name = insee_folder + '/' +  _hash(name)
        
        if (not os.path.exists(file_name)) | (update is True):
          
            if polygon is None:
                
                topic = 'administratif'
                # identifier = 'LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:departement'
                identifier = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
                
                service = 'WFS'
                Version = "2.0.0"
                    
                geoportail = 'https://wxs.ign.fr/{}/geoportail'.format(topic)
                Service = 'SERVICE=' + "WFS" + '&'
                version = 'VERSION=' + Version + '&'
                request = 'REQUEST=GetFeature&'
                typename = 'TYPENAME=' + identifier + '&'
                     
                link = geoportail + '/wfs?' + Service + version + request + typename \
                            + 'OUTPUTFORMAT=application/json&COUNT=1000' 
                  
                data = requests.get(link)
                
                if data.status_code != 200:
                    raise ValueError(data.text)
                    
                data_json = data.json()
                json = data_json['features']        
                
                df = _geojson_parser(json)
                    
                dep_poly = MultiPolygon(list(df['geometry']))
                bounds = dep_poly.bounds
                
                bbox_list0 = [poly.bounds for poly in df['geometry']]
                poly_list = []
                for i in range(len(bbox_list0)):
                    l = bbox_list0[i]
                    square = [Point(l[0],l[1]),
                            Point(l[2],l[1]),                                       
                            Point(l[2],l[3]),
                            Point(l[0],l[3])]   
                    poly = Polygon([[p.x, p.y] for p in square])
                    poly_list.append(poly)
                    
                multipoly_bounds = MultiPolygon(poly_list)
                
                # create boxes with 1 unit longitude width, 2 units latitude height 
                list_x = list(range(round(bounds[0])-5, round(bounds[2])+5))
                list_y = list(np.arange(round(bounds[1])-5, round(bounds[3])+5, 1.5))
                
                poly_grid_list = []
                for x in range(len(list_x)-1):
                    for y in range(len(list_y)-1):
                         square = [Point(list_x[x], list_y[y]),                       
                            Point(list_x[x+1], list_y[y]),                                       
                            Point(list_x[x+1], list_y[y+1]),
                            Point(list_x[x], list_y[y+1])]  
                         
                         poly = Polygon([[p.x, p.y] for p in square])
                         # poly_grid_list.append(poly)
                         # if the polygon intersects france multipolygon
                         # it is added to the polygon grid list
                         if poly.intersects(multipoly_bounds):
                             poly_grid_list.append(poly)
                             
                bbox_list_final = [poly.bounds for poly in poly_grid_list]
            
             # MultiPolygon(poly_grid_list)   
            else:
                bbox = _get_bbox_list(polygon=None, update=update)
                bbox_list_final = []
                for i in range(len(bbox)):
                    square = [Point(bbox[i][0], bbox[i][1]),
                                 Point(bbox[i][2], bbox[i][1]),   
                                 Point(bbox[i][2], bbox[i][3]),   
                                 Point(bbox[i][0], bbox[i][3])] 
                    
                    poly_bbox = Polygon([[p.x, p.y] for p in square])
                    
                    # select only intersect between bbox grid and the polygon
                    if polygon.intersects(poly_bbox):
                        
                        intersection = polygon.intersection(poly_bbox) 
                        
                        list_intersect_bounds = [intersection.geoms[i].bounds for i in range(len(intersection.geoms))]
                        
                        for p in range(len(list_intersect_bounds)):
                            if list_intersect_bounds[p] not in bbox_list_final:
                                bbox_list_final.append(list_intersect_bounds[p])
                
            open_file = open(file_name, "wb")
            pickle.dump(bbox_list_final, open_file)
            open_file.close()
    
        else:        
            try:
                open_file = open(file_name, "rb")
                bbox_list_final = pickle.load(open_file)
                open_file.close()
            except:
                os.remove(file_name)
                bbox_list_final = _get_bbox_list(polygon=polygon,
                                                 update=True)
    except:
        name = '_get_bbox_list'
        
        if polygon is not None:
            name += ''.join([str(i) for i in list(polygon.bounds)])
                
        insee_folder = _create_insee_folder()
        file_name = insee_folder + '/' +  _hash(name)
        
        bbox_list_final = [(-62.0, 13.0, -61.0, 14.5),
                            (-62.0, 14.5, -61.0, 16.0),
                            (-62.0, 16.0, -61.0, 17.5),
                            (-61.0, 13.0, -60.0, 14.5),
                            (-61.0, 14.5, -60.0, 16.0),
                            (-55.0, 1.0, -54.0, 2.5),
                            (-55.0, 2.5, -54.0, 4.0),
                            (-55.0, 4.0, -54.0, 5.5),
                            (-55.0, 5.5, -54.0, 7.0),
                            (-54.0, 1.0, -53.0, 2.5),
                            (-54.0, 2.5, -53.0, 4.0),
                            (-54.0, 4.0, -53.0, 5.5),
                            (-54.0, 5.5, -53.0, 7.0),
                            (-53.0, 1.0, -52.0, 2.5),
                            (-53.0, 2.5, -52.0, 4.0),
                            (-53.0, 4.0, -52.0, 5.5),
                            (-53.0, 5.5, -52.0, 7.0),
                            (-52.0, 1.0, -51.0, 2.5),
                            (-52.0, 2.5, -51.0, 4.0),
                            (-52.0, 4.0, -51.0, 5.5),
                            (-52.0, 5.5, -51.0, 7.0),
                            (-6.0, 47.5, -5.0, 49.0),
                            (-5.0, 47.5, -4.0, 49.0),
                            (-4.0, 46.0, -3.0, 47.5),
                            (-4.0, 47.5, -3.0, 49.0),
                            (-3.0, 46.0, -2.0, 47.5),
                            (-3.0, 47.5, -2.0, 49.0),
                            (-2.0, 41.5, -1.0, 43.0),
                            (-2.0, 43.0, -1.0, 44.5),
                            (-2.0, 44.5, -1.0, 46.0),
                            (-2.0, 46.0, -1.0, 47.5),
                            (-2.0, 47.5, -1.0, 49.0),
                            (-2.0, 49.0, -1.0, 50.5),
                            (-1.0, 41.5, 0.0, 43.0),
                            (-1.0, 43.0, 0.0, 44.5),
                            (-1.0, 44.5, 0.0, 46.0),
                            (-1.0, 46.0, 0.0, 47.5),
                            (-1.0, 47.5, 0.0, 49.0),
                            (-1.0, 49.0, 0.0, 50.5),
                            (0.0, 41.5, 1.0, 43.0),
                            (0.0, 43.0, 1.0, 44.5),
                            (0.0, 44.5, 1.0, 46.0),
                            (0.0, 46.0, 1.0, 47.5),
                            (0.0, 47.5, 1.0, 49.0),
                            (0.0, 49.0, 1.0, 50.5),
                            (1.0, 41.5, 2.0, 43.0),
                            (1.0, 43.0, 2.0, 44.5),
                            (1.0, 44.5, 2.0, 46.0),
                            (1.0, 46.0, 2.0, 47.5),
                            (1.0, 47.5, 2.0, 49.0),
                            (1.0, 49.0, 2.0, 50.5),
                            (1.0, 50.5, 2.0, 52.0),
                            (2.0, 41.5, 3.0, 43.0),
                            (2.0, 43.0, 3.0, 44.5),
                            (2.0, 44.5, 3.0, 46.0),
                            (2.0, 46.0, 3.0, 47.5),
                            (2.0, 47.5, 3.0, 49.0),
                            (2.0, 49.0, 3.0, 50.5),
                            (2.0, 50.5, 3.0, 52.0),
                            (3.0, 41.5, 4.0, 43.0),
                            (3.0, 43.0, 4.0, 44.5),
                            (3.0, 44.5, 4.0, 46.0),
                            (3.0, 46.0, 4.0, 47.5),
                            (3.0, 47.5, 4.0, 49.0),
                            (3.0, 49.0, 4.0, 50.5),
                            (3.0, 50.5, 4.0, 52.0),
                            (4.0, 43.0, 5.0, 44.5),
                            (4.0, 44.5, 5.0, 46.0),
                            (4.0, 46.0, 5.0, 47.5),
                            (4.0, 47.5, 5.0, 49.0),
                            (4.0, 49.0, 5.0, 50.5),
                            (4.0, 50.5, 5.0, 52.0),
                            (5.0, 41.5, 6.0, 43.0),
                            (5.0, 43.0, 6.0, 44.5),
                            (5.0, 44.5, 6.0, 46.0),
                            (5.0, 46.0, 6.0, 47.5),
                            (5.0, 47.5, 6.0, 49.0),
                            (5.0, 49.0, 6.0, 50.5),
                            (6.0, 41.5, 7.0, 43.0),
                            (6.0, 43.0, 7.0, 44.5),
                            (6.0, 44.5, 7.0, 46.0),
                            (6.0, 46.0, 7.0, 47.5),
                            (6.0, 47.5, 7.0, 49.0),
                            (6.0, 49.0, 7.0, 50.5),
                            (7.0, 43.0, 8.0, 44.5),
                            (7.0, 44.5, 8.0, 46.0),
                            (7.0, 46.0, 8.0, 47.5),
                            (7.0, 47.5, 8.0, 49.0),
                            (7.0, 49.0, 8.0, 50.5),
                            (8.0, 40.0, 9.0, 41.5),
                            (8.0, 41.5, 9.0, 43.0),
                            (8.0, 43.0, 9.0, 44.5),
                            (8.0, 47.5, 9.0, 49.0),
                            (8.0, 49.0, 9.0, 50.5),
                            (9.0, 40.0, 10.0, 41.5),
                            (9.0, 41.5, 10.0, 43.0),
                            (9.0, 43.0, 10.0, 44.5),
                            (45.0, -14.0, 46.0, -12.5),
                            (55.0, -21.5, 56.0, -20.0)]
        
        if polygon is not None:
            open_file = open(file_name, "wb")
            pickle.dump(bbox_list_final, open_file)
            open_file.close()
            
        
    
    return(bbox_list_final)