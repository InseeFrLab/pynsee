import functools
import os
import pandas as pd
import warnings
import shapely
from shapely.errors import ShapelyDeprecationWarning
import warnings

from pynsee.utils._warning_cached_data import _warning_cached_data
from pynsee.utils._create_insee_folder import _create_insee_folder
from pynsee.utils._hash import _hash
from geopyx.utils._print import _print

def save_df(obj=pd.DataFrame, print_cached_data=True, parquet=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            
            data_folder = _create_insee_folder()
            string_file_arg = [str(kwargs[a]) for a in kwargs.keys() if a != 'update'] + \
                                [func.__name__] + [str(a) for a in args]            
            file_name = data_folder + "/" + _hash(''.join(string_file_arg)) 
            
            if parquet:
                file_name += ".parquet"
            else:
                file_name += ".pkl"            
                                    
            if any([(a == 'update') & (kwargs[a] == True) for a in kwargs.keys()]):
                update = True
            else:
                update = False
            
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

                if (not os.path.exists(file_name, data_folder)) | (update is True):   

                    df = func(*args, **kwargs)                    
                    try:
                        if parquet:
                            df.to_parquet(file_name)
                        else:
                            df.to_csv(file_name, index=False)
                            
                    except Exception as e:
                        warnings.warn(str(e))
                        print(f'Error, file not saved:\n{file_name}\n{df}')
                        print(type(df))
                        print('\n')
                    
                    df = obj(df) 
                    
                    if print_cached_data:
                        print(f"Data saved: {file_name}")

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
                        
                        print('!!! Unable to load data, function retriggered !!!')
                        
                        df = func(*args, **kwargs2)
                        df = obj(df)   
                    else:
                        if print_cached_data:
                            _warning_cached_data(file_name)
                        df = obj(df)            
            
            return df
        return wrapper
    return decorator