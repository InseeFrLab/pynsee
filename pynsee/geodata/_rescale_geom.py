from shapely.affinity import scale
import warnings
from shapely.errors import ShapelyDeprecationWarning

from pynsee.geodata._get_center import _get_center


def _rescale_geom(df, factor, col="geometry"):

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

        center = _get_center(df, col=col)

        list_geoms = []
        for i in range(len(df["geometry"])):
            list_geoms += [
                scale(
                    geom=df.loc[i, "geometry"],
                    xfact=factor,
                    yfact=factor,
                    zfact=1.0,
                    origin=center,
                )
            ]

        df["geometry"] = list_geoms

        return df
