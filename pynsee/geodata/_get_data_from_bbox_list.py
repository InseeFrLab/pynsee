import asyncio
import aiohttp
from itertools import chain

from pynsee.utils.requests_params import _get_requests_headers
from pynsee.geodata._distance import _distance

async def _get_data_from_bbox_list(list_bbox, id):

    urls = []
    
    for bbox in list_bbox:    

        urls += [make_geodata_query(bbox, id = id)]
        
    all_results = []
    
    while (len(urls) > 0):
        print('\n')
        print(list_bbox)
        r = await _get_all_queries(urls)
    
        list_retries = []
        # select queries whose results are full
        for k in r.keys():
            if len(r[k]['features']) == 1000:
                list_retries += [k]
            else:
                all_results += [r[k]['features']]
    
        if len(list_retries) > 0:
            # to avoid missing data bbox should be splitted
            # and queries should be launched again
            list_bbox_retry = [elem for i, elem in enumerate(list_bbox) if i in list_retries]
            
            # split bbox
            list_bbox = flatten_chain([_get_splitted_bbox(bbox) for bbox in list_bbox_retry])
    
            # make new queries
            urls = [make_geodata_query(bbox) for bbox in list_bbox]
        else:
            urls = []

    return all_results
 

def flatten_chain(list_obj):
    return list(chain.from_iterable(list_obj))
    

async def get_all_queries(urls):

    # reference from stackoverflow
    # https://stackoverflow.com/questions/76244656/why-does-aiohttp-clientsession-object-get-method-return-results-in-order-ev
    # by D.L
    
    res_dict = {}

    # list of tasks (with the gather)
    tasks = [asyncio.create_task(get_response(url)) for url in urls]
    responses = await asyncio.gather(*tasks)

    # make the dict
    for i, response in enumerate(responses):
        res_dict[i] = response
        
    return res_dict

async def get_response(url):
    ''' async func for the reqest '''
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json() 

def make_geodata_query(
        bbox,
        crsPolygon="EPSG:4326",
        id = "ADMINEXPRESS-COG-CARTO.LATEST:commune"):
    
    service = "WFS"
    Version = "2.0.0"
    crs="EPSG:3857"    
    
    geoportail = f"https://data.geopf.fr/{service.lower()}/ows?"
    Service = "SERVICE=" + service + "&"
    version = "VERSION=" + Version + "&"
    request = "REQUEST=GetFeature&"
    typename = "TYPENAME=" + id + "&"
    Crs = "srsName=" + crs + "&"
    
    link0 = (
        geoportail
        + Service
        + version
        + request
        + typename
        + Crs
        + "OUTPUTFORMAT=application/json&COUNT=1000"
    )
    
    bounds = [
            str(bbox[1]),
            str(bbox[0]),
            str(bbox[3]),
            str(bbox[2]),
            "urn:ogc:def:crs:" + crsPolygon,
        ]
    
    BBOX = "&BBOX={}".format(",".join(bounds))

    return link0 + BBOX

def _get_splitted_bbox(bbox):
    width = _distance(
                    (bbox[0], bbox[1]), (bbox[2], bbox[1])
                )
    height = _distance(
        (bbox[0], bbox[1]), (bbox[0], bbox[3])
    )

    if width > height:
        bbox1 = [
            bbox[0],
            bbox[1],
            (bbox[2] + bbox[0]) / 2,
            bbox[3],
        ]

        bbox2 = [
            (bbox[2] + bbox[0]) / 2,
            bbox[1],
            bbox[2],
            bbox[3],
        ]
    else:
        bbox1 = [
            bbox[0],
            bbox[1],
            bbox[2],
            (bbox[1] + bbox[3]) / 2,
        ]

        bbox2 = [
            bbox[0],
            (bbox[1] + bbox[3]) / 2,
            bbox[2],
            bbox[3],
        ]
    return [bbox1, bbox2]

if __name__ == '__main__':
    from pynsee.geodata._get_bbox_list_full import _get_bbox_list_full
    
    _get_splitted_bbox([1.0, 49.0, 2.0, 55])
    bbox_list = [(1.0, 49.0, 2.0, 55)]
    bbox_list  += _get_bbox_list_full()
    bbox_list = bbox_list[:10]
    id = "ADMINEXPRESS-COG-CARTO.LATEST:commune"

    results = await _get_data_from_bbox_list(bbox_list, id = id)


