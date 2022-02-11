
def translate_overseas(self):
    
    communes['geometry'] = communes['geometry'].to_list()
    list_ovdep = ['971', '972', '973', '974', '976']
    fm = communes[~communes['departement_code'].isin(list_ovdep)]
    fm = fm.reset_index(drop=True)


    dep29 =  communes[communes['departement_code'].isin(['29'])]
    dep29 = dep29.reset_index(drop=True)
    minx = min(_extract_bounds(geom=dep29['geometry'], var='minx'))
    miny = min(_extract_bounds(geom=dep29['geometry'], var='miny')) + 3

    list_new_dep = []         

    for d in range(len(list_ovdep)):
        ovdep = communes[communes['departement_code'].isin([list_ovdep[d]])]
        ovdep = ovdep.reset_index(drop=True)
        if list_ovdep[d] == '973':
            # area divided by 4 for Guyane
            ovdep = _rescale_geom(df=ovdep, factor = 0.25)

        maxxdep = max(_extract_bounds(geom=ovdep['geometry'], var='maxx'))
        maxydep = max(_extract_bounds(geom=ovdep['geometry'], var='maxy'))
        xoff = minx - maxxdep - 2.5
        yoff = miny - maxydep
        ovdep['geometry'] = ovdep['geometry'].apply(lambda x: translate(x, xoff=xoff, yoff=yoff))


        miny = min(_extract_bounds(geom=ovdep['geometry'], var='miny')) - 1.5
        list_new_dep.append(ovdep)

        # PARIS