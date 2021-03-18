# -*- coding: utf-8 -*-

def get_insee_definition(ids):
    
    from pynsee.utils._request_insee import _request_insee
    
    import re
    import pandas as pd
    
    #ids = ['c1020', 'c1601']
    
    link = 'https://api.insee.fr/metadonnees/V1/concepts/definition'
    
    list_data = []
    
    def clean_definition(string):
        m = re.search("\\<p\\>.*\\<\\/p\\>", string)
        if m:
            string_selected = m.group(0)
            string_cleaned = string_selected.replace("<p>", "").replace("</p>", "").replace(u'\xa0', u' ')
        else:
            string_cleaned = string
        return(string_cleaned)
    
    def extract_data(data, item1, i , item2):
        try:
            val = data[item1][i][item2]
        except:
            val = None
        return(val)
    
    for id in ids:
        
        query = link + '/' + id
    
        request = _request_insee(api_url = query, file_format = 'application/json')
        
        data = request.json()          

        title_fr = None
        title_en = None
        
        try:
            if data['intitule'][0]['langue'] == 'fr':
                title_fr = extract_data(data, item1='intitule', i=0, item2='contenu')            
                title_en = extract_data(data, item1='intitule', i=1, item2='contenu')
        except:
            pass
       
        def_fr = None
        def_en = None
        
        try:
            if data['definition'][0]['langue'] == 'fr':
                def_fr = extract_data(data, item1='definition', i=0, item2='contenu')
                def_en = extract_data(data, item1='definition', i=1, item2='contenu')                
                def_fr = clean_definition(def_fr)
                def_en = clean_definition(def_en)
        except:
            pass
        
        def_short_fr = None
        def_short_en = None
        
        try:
            if data['definitionCourte'][0]['langue'] == 'fr':
                def_short_fr = extract_data(data, item1='definitionCourte', i=0, item2='contenu')
                def_short_en = extract_data(data, item1='definitionCourte', i=1, item2='contenu')
                def_short_fr = clean_definition(def_fr)
                def_short_en = clean_definition(def_en)
        except:
            pass
        
        update = None
        
        try:
            update = data['dateMiseAJour']
        except:
            pass
        
        uri = None
        
        try:
            uri = data['uri']
        except:
            pass
        
        df = pd.DataFrame(
                {'id':id,
                 'title_fr':title_fr,
                 'title_en':title_en,                
                 'def_short_fr':def_short_fr,
                 'def_short_en':def_short_en,
                 'def_fr':def_fr,
                 'def_en':def_en,
                 'update':update, 
                 'uri':uri}, index=[0])
        
        list_data.append(df)
       
    data_final = pd.concat(list_data)
     
    return(data_final)           