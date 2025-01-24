# -*- coding: utf-8 -*-

import pandas as pd
from shapely.geometry import shape
import warnings

import logging

logger = logging.getLogger(__name__)


def _geojson_parser(data):

    data_list = []
    list_shapes = []

    for c in range(len(data)):

        df = data[c]["properties"]

        df2 = pd.DataFrame(
            {
                f: df[f]
                for f in df.keys()
                if f not in (["geometry", "bbox"])
                and (type(df[f]) is not list)
            },
            index=[0],
        )

        for k in df.keys():
            dfk = df[k]
            if type(dfk) is list:
                try:
                    df2[k] = [df[k]]
                except Exception:
                    pass

        geom = data[c]["geometry"]["coordinates"]

        data_type = data[c]["geometry"]["type"]

        try:
            if "id" not in df2.columns:
                df2["id"] = data[c]["id"]
        except Exception:
            pass

        Shape = shape({"type": data_type, "coordinates": geom})
        # list_shapes = [Shape.geoms[x] for x in range(len(Shape.geoms))]

        if data_type in [
            "MultiLineString",
            "MultiPolygon",
            "MultiPoint",
            "LineString",
            "Polygon",
            "Point",
        ]:
            list_shapes += [Shape]
            data_list.append(df2)
        else:
            logger.warning(f"Unsupported shape {data_type} has been removed")

    data_all = pd.concat(data_list)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data_all["geometry"] = list_shapes

    return data_all
