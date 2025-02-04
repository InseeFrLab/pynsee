from shapely.affinity import scale

from ._get_center import _get_center


def _rescale_geom(gdf, factor):
    center = _get_center(gdf)

    list_geoms = []
    for i in range(len(gdf.geometry)):
        list_geoms += [
            scale(
                geom=gdf.loc[i, "geometry"],
                xfact=factor,
                yfact=factor,
                zfact=1.0,
                origin=center,
            )
        ]

    gdf["geometry"] = list_geoms

    return gdf
