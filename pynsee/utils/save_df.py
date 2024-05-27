import functools
import os
import pandas as pd
import warnings
import shapely
from shapely.errors import ShapelyDeprecationWarning
import warnings
import datetime 
import logging
logger = logging.getLogger(__name__)

from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash

@functools.lru_cache(maxsize=None)
def _warning_cached_data(file, mdate=None, day_lapse=None):
    strg_print = f"Previously saved data has been used:\n{file}\n"
    if (mdate is not None) and (day_lapse is not None):
        strg_print += f"Creation date: {mdate:%Y-%m-%d}"
        
        if day_lapse >= 2:
            strg_print += f", {day_lapse} days ago\n"
        if day_lapse == 1:
            strg_print += ", yesterday\n"
        if day_lapse == 0:
            strg_print += ", today\n"
            
    strg_print += "Set update=True to get the most up-to-date data"

    logger.info(strg_print)

def save_df(obj=pd.DataFrame, parquet=True, day_lapse_max=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            
            data_folder = _create_insee_folder()
            string_file_arg = [str(kwargs[a]) for a in kwargs.keys() if a not in ['update', 'silent']]
            string_file_arg += [func.__name__] + [str(a) for a in args]            
            file_name = os.path.join(data_folder, _hash(''.join(string_file_arg)))
            
            if parquet:
                file_name += ".parquet"
            else:
                file_name += ".pkl"            
                                    
            update = kwargs.get("update", False)

            silent = kwargs.get("silent", False)
            
            if os.path.exists(file_name):
                file_date_last_modif = datetime.datetime.fromtimestamp(
                    os.path.getmtime(file_name)
                )

                insee_date_time_now = kwargs.get(
                    "insee_date_test", datetime.datetime.now())

                day_lapse = (insee_date_time_now - file_date_last_modif).days

                if day_lapse_max is not None:
                    if day_lapse > day_lapse_max:
                        update = True                    
            
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

                if (not os.path.exists(file_name)) or update:   

                    df = func(*args, **kwargs)                    
                    try:
                        if parquet:
                            df.to_parquet(file_name)
                        else:
                            df.to_csv(file_name, index=False)
                            
                    except Exception as e:
                        warnings.warn(str(e))
                        warnings.warn(f'Error, file not saved:\n{file_name}\n{df}')
                        warnings.warn('\n')
                                        
                    if not silent:
                        logger.info(f"Data saved:\n{file_name}")

                else:
                    try:                        
                        if parquet:
                            df = pd.read_parquet(file_name)
                        else:
                            df = pd.read_pickle(file_name)
                            
                        if 'Unnamed: 0' in df.columns:
                            del df['Unnamed: 0']
                            
                    except Exception as e:
                        warnings.warn(str(e))
                                                
                        kwargs2 = kwargs
                        kwargs2['update'] = True
                        
                        warnings.warn('!!! Unable to load data, function retriggered !!!')
                        
                        df = func(*args, **kwargs2)                         
                    else:
                        if not silent:
                            
                            mdate = insee_date_time_now - datetime.timedelta(days=day_lapse)
                            
                            _warning_cached_data(file_name,
                                                 mdate= mdate,
                                                 day_lapse=day_lapse)
            
            return obj(df)  
        return wrapper
    return decorator