
import multiprocessing
import tqdm

from pynsee.geodata._convert_polygon import _convert_polygon_list
from pynsee.geodata._convert_polygon import _set_global_translate_overseas

def _convert_main(mainGeo, file_geodata):

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

    mainGeo.to_pickle(file_geodata)

    return mainGeo