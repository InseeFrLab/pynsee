# -*- coding: utf-8 -*-

def _get_insee_local(variables, dataset, codegeo, geo):
    
    from pynsee.utils._request_insee import _request_insee
    from pynsee.utils._paste import _paste
    
    import pandas as pd
    
#    variables = 'AGESCOL-SEXE-ETUD';dataset = 'GEO2019RP2011';codegeo = '91';geo = 'DEP'
    
    if type(variables) == list:
        variables = _paste(variables, collapse = '-')
        
    count_sep = variables.count('-')
    modalite = '.all' * (count_sep+1)
    
    link = 'https://api.insee.fr/donnees-locales/V0.1/donnees/'
    link = link + 'geo-{}@{}/{}-{}{}'.format(variables, dataset, geo, codegeo, modalite)
    
    request = _request_insee(api_url = link, file_format = 'application/json;charset=utf-8')
    
    data_request = request.json()
    
    Cellule = data_request['Cellule']
    Variable = data_request['Variable']
    Croisement = data_request['Croisement']
    Zone = data_request['Zone']
    
    dataset_version = Croisement['JeuDonnees']['@code']
    dataset_name = Croisement['JeuDonnees']['Source']
    data_date = Croisement['JeuDonnees']['Annee']
    geo_date = Zone['Millesime']['@annee']
    codegeo_label = Zone['Millesime']['Nccenr']
    
    list_data = []
    
    for i in range(len(Cellule)):
        dico = {**Cellule[i]['Zone'], **Cellule[i]['Mesure']}
        modalite = Cellule[i]['Modalite']
        
        for m in range(len(modalite)):
            dico_added = {modalite[m]['@variable']: modalite[m]['@code']}
            dico = {**dico, **dico_added}
            
        dico['OBS_VALUE'] =  Cellule[i]['Valeur']
        df = pd.DataFrame(dico, index=[0])
        list_data.append(df)
        
    data = pd.concat(list_data)
            
    for i in range(len(Variable)):
        df = pd.DataFrame(Variable[i]['Modalite'])
        var_name = Variable[i]['@code']
        df = df[['@code', 'Libelle']]
        df.columns = [var_name, var_name + '_label']
        data = data.merge(df, on = var_name, how = 'left')
    
    data = data.assign(DATASET_VERSION = dataset_version,
                       DATASET_NAME = dataset_name,
                       DATA_DATE = data_date,
                       GEO_DATE = geo_date,
                       CODEGEO_LABEL = codegeo_label)
    
    data.rename(columns={'@codgeo':'CODEGEO',
                         '@nivgeo':'NIVGEO',
                         '@code':'UNIT',
                         '$':'UNIT_label'}, inplace=True)
    
    data['OBS_VALUE'] = pd.to_numeric(data['OBS_VALUE'])
    data['DATA_DATE'] = pd.to_numeric(data['DATA_DATE'])
    data['GEO_DATE'] = pd.to_numeric(data['GEO_DATE'])
     
    return(data)
           