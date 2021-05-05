
import pandas as pd
import csv
from functools import lru_cache

from pynsee.utils._request_insee import _request_insee

@lru_cache(maxsize=None)
def _get_data_from_query_csv(link, kind):

    request = _request_insee(api_url = link, file_format = 'text/csv')
    
    decoded_content = request.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    
    df = pd.DataFrame(list(cr))
    
    df.columns = list(df.loc[0,:])
    df = df.iloc[1:]
    
    return(df)