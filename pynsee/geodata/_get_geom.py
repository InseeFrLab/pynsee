from shapely.geometry import (
    Point,
    Polygon,
    MultiPolygon,
    LineString,
    MultiLineString,
    MultiPoint,
)


def _get_geom(df, col="geometry"):

    df = df.reset_index(drop=True)

    if col in df.columns:
        geoList = []
        geoListType = []

        none_detected = False

        for i in range(len(df.index)):
            poly = df[col][i]
            if type(poly) in [Polygon, Point, LineString]:
                geoList += [poly]
                geoListType.append(type(poly))
            elif type(poly) in [MultiPolygon, MultiLineString, MultiPoint]:
                for j in range(len(poly.geoms)):
                    geoList += [poly.geoms[j]]
                geoListType.append(type(poly))
            else:
                none_detected = True

        if none_detected:
            shapes = ["MultiPolygon", "MultiLineString", "MultiPoint"] + [
                "Polygon",
                "Point",
                "LineString",
            ]
            print(
                "!!! one shape in geometry column is not among supported shapely classes or is None:\n %s"
                % ", ".join(shapes)
            )

        geoListType = list(dict.fromkeys(geoListType))

        if all([x in [MultiPolygon, Polygon] for x in geoListType]):
            geo = MultiPolygon(geoList)
        elif all([x in [MultiPoint, Point] for x in geoListType]):
            geo = MultiPoint(geoList)
        elif all([x in [MultiLineString, LineString] for x in geoListType]):
            geo = MultiLineString(geoList)
        else:
            raise ValueError("!!! geometry column mixes shapely classes !!!")
    else:
        raise ValueError("!!! geometry column is missing !!!")

    return geo
