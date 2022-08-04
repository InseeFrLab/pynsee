def _convert_polygon(geo, crs_in="EPSG:4326", crs_out="EPSG:3857"):

    import pyproj
    from shapely.ops import transform

    crsIn = pyproj.CRS(crs_in)
    crsOut = pyproj.CRS(crs_out)

    project = pyproj.Transformer.from_crs(crsIn, crsOut, always_xy=True).transform
    geo_converted = transform(project, geo)

    return geo_converted
