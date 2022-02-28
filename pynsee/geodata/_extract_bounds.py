
def _extract_bounds(polygon, var):
    if var == 'minx':
        i = 0
    elif var == 'miny':
        i = 1
    elif var == 'maxx':
        i = 2
    elif var == 'maxy':
        i = 3
    
    polygon_bounds = [polygon.geoms[j].bounds for j in range(len(polygon.geoms))]
    val = [polygon_bounds[j][i] for j in range(len(polygon.geoms))]
    
    return(val)
