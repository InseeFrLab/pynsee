
import pandas as pd
from shapely.affinity import translate

from pynsee.geodata._extract_bounds import _extract_bounds
from pynsee.geodata._rescale_geom import _rescale_geom

def translate_overseas(self, guyaneFactor=0.25):
    
    df = self

    if all([x in df.columns for x in ['insee_dep', 'geometry']]):

        list_ovdep = ['971', '972', '973', '974', '976']
        fm = df[~df['insee_dep'].isin(list_ovdep)]
        fm = fm.reset_index(drop=True)
        
        dep29 = df[df['insee_dep'].isin(['29'])]
        dep29 = dep29.reset_index(drop=True)
        minx = min(_extract_bounds(geom=dep29['geometry'], var='minx'))
        miny = min(_extract_bounds(geom=dep29['geometry'], var='miny')) + 3

        list_new_dep = []         

        for d in range(len(list_ovdep)):
            ovdep = df[df['insee_dep'].isin([list_ovdep[d]])]
            ovdep = ovdep.reset_index(drop=True)
            if list_ovdep[d] == '973':
                # area divided by 4 for Guyane
                ovdep = _rescale_geom(df=ovdep, factor = guyaneFactor)

            maxxdep = max(_extract_bounds(geom=ovdep['geometry'], var='maxx'))
            maxydep = max(_extract_bounds(geom=ovdep['geometry'], var='maxy'))
            xoff = minx - maxxdep - 2.5
            yoff = miny - maxydep
            ovdep['geometry'] = ovdep['geometry'].apply(lambda x: translate(x, xoff=xoff, yoff=yoff))


            miny = min(_extract_bounds(geom=ovdep['geometry'], var='miny')) - 1.5
            list_new_dep.append(ovdep)
        
        df = pd.concat(list_new_dep + [fm])
    
    return df

    
    
    
    