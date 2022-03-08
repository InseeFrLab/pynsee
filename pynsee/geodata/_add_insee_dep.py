from tqdm import trange
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString, MultiPoint
from pandas.api.types import CategoricalDtype

from pynsee.geodata.get_geodata import get_geodata
from pynsee.geodata._get_center import _get_center
#from pynsee.geodata._get_overseas_bbox_list import _get_overseas_bbox_list

def _add_insee_dep(df):
    
    df = df.reset_index(drop=True)
    
    #ov_bbox = _get_overseas_bbox_list()
    #bbox = ov_bbox['bbox'].to_list()
    #list_geo_ov = [Polygon([Point(bbox[i][0], bbox[i][1]),
    #                        Point(bbox[i][2], bbox[i][1]),   
    #                        Point(bbox[i][2], bbox[i][3]),   
    #                       Point(bbox[i][0], bbox[i][3])]) for i in range(len(bbox))]
        
    list_dep = []
    list_dep_center = []
       
    for i in trange(len(df.index), desc='Finding departement'):
        geo = df.loc[i, 'geometry']
        dep = None
        dep_center = None
        
        #for i_poly_ov in range(len(list_geo_ov)):        
        #    if geo.intersects(list_geo_ov[i_poly_ov]):
        #        dep = ov_bbox.loc[i_poly_ov, 'insee_dep']
        #        dep_center = _extract_center(list_geo_ov[i_poly_ov])
                
        if dep is None:
            try:
                dep_list = get_geodata('ADMINEXPRESS-COG.LATEST:departement')
                list_ovdep = ['971', '972', '974', '973', '976']
                list_other_dep = [d for d in dep_list.insee_dep if d not in list_ovdep]
                dep_order = list_ovdep + list_other_dep
                
                dep_list["insee_dep"] = dep_list["insee_dep"].astype(
                    CategoricalDtype(categories=dep_order, ordered=True))
                dep_list = dep_list.sort_values(["insee_dep"]).reset_index(drop=True)
                
                for j in dep_list.index:
                    depgeo = dep_list.loc[j, 'geometry']
                    if geo.intersects(depgeo):
                        dep = dep_list.loc[j, 'insee_dep']
                        dep_center = _extract_center(depgeo)
                        break
            except:
                pass
                        
        list_dep += [dep]
        list_dep_center += [dep_center]
    
    df['insee_dep'] = list_dep
    df['insee_dep_center'] = list_dep_center
    
    return df
