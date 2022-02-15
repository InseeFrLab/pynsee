
def _extract_bounds(geom, var):
    if var == 'minx':
        i = 0
    elif var == 'miny':
        i = 1
    elif var == 'maxx':
        i = 2
    elif var == 'maxy':
        i = 3
    
    geom_bounds = [geom[j].bounds for j in range(len(geom))]
    val = [geom_bounds[j][i] for j in range(len(geom))]
    
    return(val)