
import pandas as pd
from shapely.affinity import translate

from pynsee.geodata._extract_bounds import _extract_bounds
from pynsee.geodata._rescale_geom import _rescale_geom

def zoom_paris(self):

    df = self

    if all([x in df.columns for x in ['insee_dep', 'geometry']]):
        
        paris = df[df['insee_dep'].isin(['75','92', '93','94'])]        
        paris = paris.reset_index(drop=True)
        paris = _rescale_geom(df = paris, factor = 4)
        
        dep29 =  df[df['insee_dep'].isin(['29'])]
        dep29 = dep29.reset_index(drop=True)
        minx = min(_extract_bounds(geom=dep29['geometry'], var= 'minx'))
        miny = min(_extract_bounds(geom=dep29['geometry'], var= 'miny')) + 3
        
        maxxdep = max(_extract_bounds(geom=paris['geometry'], var= 'maxx'))
        maxydep = max(_extract_bounds(geom=paris['geometry'], var= 'maxy'))
        xoff = minx - maxxdep + 1
        yoff = miny - maxydep - 5
        paris['geometry'] = paris['geometry'].apply(lambda x: translate(x, xoff=xoff, yoff=yoff))

        df = pd.concat([self, paris])                

    return df