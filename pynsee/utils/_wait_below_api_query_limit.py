# -*- coding: utf-8 -*-


def _wait_below_api_query_limit(query):
    
    import os, time
    import pandas as pd
    from datetime import datetime
    from tqdm import trange
    
    from pynsee.utils._create_insee_folder import _create_insee_folder
    from pynsee.utils._hash import _hash
    
    max_query_insee_api = 30
    timespan_insee_api = 60
    
    insee_folder = _create_insee_folder()
    
    file = insee_folder + '/' + _hash('queries_count')
    
    date_time_now = datetime.now()
    
    if not os.path.exists(file):
        
        qCount = pd.DataFrame({
                "query" : query,
                "run_time" : date_time_now                
                }, index=[0])
    
        qCount.to_pickle(file)
        
    else:
        try:
            qCount = pd.read_pickle(file) 
            
            for r in range(len(qCount.index)):
                qCount.loc[r, 'time_gap'] = (date_time_now - qCount.loc[r, 'run_time']).seconds
                qCount.loc[r, 'oneMin'] = (qCount.loc[r, 'time_gap'] < timespan_insee_api)
        
            qCount = qCount.loc[qCount['oneMin'] == True]
            n_query = len(qCount.index)
            
            if n_query >= max_query_insee_api-1:
                
                oldest_query_time_gap = max(qCount['time_gap'])
                waiting_time = timespan_insee_api - oldest_query_time_gap + 1
                
                for t in trange(waiting_time, desc = "Waiting time - %s secs" % waiting_time):
                    time.sleep(1)
                            
            new_query_time = pd.DataFrame({
                    "query" : query,
                    "run_time" : date_time_now                
                    }, index=[0])
            
            qCount = qCount.append(new_query_time).reset_index()
            
            qCount.to_pickle(file)
            
        except:
            os.remove(file)
            _wait_below_api_query_limit(query)
            
        
        
            
            
            
            
            
            
            
            
            
            
        
    