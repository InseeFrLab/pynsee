import warnings


def _extract_bounds(geom, var):

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if var == "minx":
            i = 0
        elif var == "miny":
            i = 1
        elif var == "maxx":
            i = 2
        elif var == "maxy":
            i = 3

        geom_bounds = [geom.geoms[j].bounds for j in range(len(geom.geoms))]
        val = [geom_bounds[j][i] for j in range(len(geom.geoms))]

        return val
