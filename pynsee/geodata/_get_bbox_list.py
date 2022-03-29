
import os
import pickle
from shapely.geometry import Polygon, Point

from pynsee.geodata._get_bbox_list_full import _get_bbox_list_full

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

def _get_bbox_list(polygon=None, update=False):

    name = '_get_bbox_list'
        
    if polygon is not None:
        name += ''.join([str(i) for i in list(polygon.bounds)])
            
    insee_folder = _create_insee_folder()
    file_name = insee_folder + '/' +  _hash(name)
    
    bbox = _get_bbox_list_full()

    if (not os.path.exists(file_name)) | (update is True):

        bbox_list_final = []

        if polygon is not None:
        
            for i in range(len(bbox)):
                # print(i)

                square = [Point(bbox[i][0], bbox[i][1]),
                                Point(bbox[i][2], bbox[i][1]),   
                                Point(bbox[i][2], bbox[i][3]),   
                                Point(bbox[i][0], bbox[i][3])] 
                
                poly_bbox = Polygon([[p.x, p.y] for p in square])
                
                # select only intersect between bbox grid and the polygon
                if polygon.intersects(poly_bbox):
                    
                    try:
                        intersection = polygon.intersection(poly_bbox) 
                    except:
                        try:
                            polygon = polygon.buffer(0)
                            intersection = polygon.intersection(poly_bbox) 
                        except:
                            pass

                    if hasattr(intersection, 'geoms'):

                        list_intersect_bounds = [intersection.geoms[i].bounds for i in range(len(intersection.geoms))]
                        
                        for p in range(len(list_intersect_bounds)):
                            if list_intersect_bounds[p] not in bbox_list_final:
                                bbox_list_final.append(list_intersect_bounds[p])

            if len(bbox_list_final) == 0:
                bbox_list_final = bbox
        else:
            bbox_list_final = bbox

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

    return bbox_list_final