# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

import pandas as pd
import pytest
from geopandas import GeoSeries
from shapely.geometry import Polygon, MultiPolygon, Point

from pynsee.geodata.GeoFrDataFrame import GeoFrDataFrame
from pynsee.geodata.get_geodata import get_geodata
from pynsee.geodata.get_geodata_list import get_geodata_list
from pynsee.geodata._get_geodata import _get_geodata
from pynsee.geodata._get_bbox_list import _get_bbox_list

from pynsee.geodata._get_geodata_with_backup import _get_geodata_with_backup
from pynsee.geodata._find_wfs_closest_match import _find_wfs_closest_match

# manual commands for testing only on geodata module
# coverage run -m unittest tests/geodata/test_pynsee_geodata.py
# coverage report --omit=*/utils/*,*/macrodata/*,*/localdata/*,*/download/*,*/sirene/*,*/metadata/* -m


def test_find_wfs_closest_match():
    assert isinstance(_find_wfs_closest_match(), str)


def test_get_geodata_with_backup():
    gdf = _get_geodata_with_backup("ADMINEXPRESS-COG.LATEST:departement")
    assert isinstance(gdf, GeoFrDataFrame)


def test_get_geodata_short():
    square = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]

    poly_bbox = Polygon([[p.x, p.y] for p in square])
    df = _get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
        polygon=poly_bbox,
        update=True,
    )
    print(type(df))
    assert df.loc[0, "status"] == 200

    df = get_geodata_list(update=True)
    assert isinstance(df, pd.DataFrame)


def test_get_geodata_short2():
    chflieu = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:chflieu_commune",
        update=True,
    )

    assert isinstance(chflieu, GeoFrDataFrame)
    assert all(p.geom_type == "Point" for p in chflieu.geometry)

    with pytest.warns(DeprecationWarning):
        geo = chflieu.get_geom()
        assert isinstance(geo, GeoSeries)

    geo_chflieu = chflieu.translate().zoom().geometry
    assert isinstance(geo_chflieu, GeoSeries)
    assert all(p.geom_type == "Point" for p in geo_chflieu)


def test_get_geodata_short3():
    com = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune", update=True
    )
    assert isinstance(com, GeoFrDataFrame)
    assert all(isinstance(p, (Polygon, MultiPolygon)) for p in com.geometry)


def test_get_geodata_short4():
    # query with polygon and crs 4326
    dep29 = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        update=True,
        crs="EPSG:4326",
    )
    dep29 = dep29[dep29["insee_dep"] == "29"]
    assert isinstance(dep29, GeoFrDataFrame)
    geo29 = dep29.geometry
    assert all(isinstance(p, (MultiPolygon, Polygon)) for p in geo29)

    com29 = _get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
        update=True,
        polygon=geo29,
        crsPolygon="EPSG:4326",
    )
    assert isinstance(com29, GeoFrDataFrame)


def test_get_geodata_short5():

    # query with polygon and crs 3857
    dep29 = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        update=True,
        crs="EPSG:3857",
    )
    dep29 = dep29[dep29["insee_dep"] == "29"]
    assert isinstance(dep29, GeoFrDataFrame)

    geo29 = dep29.get_geom()
    assert isinstance(geo29, MultiPolygon)
    com29 = _get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
        update=True,
        polygon=geo29,
        crsPolygon="EPSG:3857",
    )
    assert isinstance(com29, GeoFrDataFrame)


def test_get_geodata_short5b():

    com = get_geodata(dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune")
    ovdep = com.translate().zoom()
    assert isinstance(ovdep, GeoFrDataFrame)
    geo_ovdep = ovdep.get_geom()
    assert isinstance(geo_ovdep, MultiPolygon)


def test_get_geodata_short6():
    # test _add_insee_dep_from_geodata
    epci = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:epci", update=True
    )
    assert isinstance(epci, GeoFrDataFrame)
    epcit = epci.translate().zoom()
    assert isinstance(epcit, GeoFrDataFrame)
    geo_epcit = epcit.get_geom()
    assert isinstance(geo_epcit, MultiPolygon)


def test_get_geodata_short7():
    # test _add_insee_dep_region
    reg = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:region", update=True
    )
    assert isinstance(reg, GeoFrDataFrame)
    regt = reg.translate().zoom()
    assert isinstance(regt, GeoFrDataFrame)
    geo_regt = regt.get_geom()
    assert isinstance(geo_regt, MultiPolygon)


def test_get_geodata_short8():
    dep = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        crs="EPSG:4326",
    )
    dep13 = dep[dep["insee_dep"] == "13"]
    geo13 = dep13.get_geom()

    bbox = _get_bbox_list(polygon=geo13, update=True, crsPolygon="EPSG:4326")
    assert isinstance(bbox, list)
    bbox = _get_bbox_list(polygon=geo13)
    assert isinstance(bbox, list)


def test_get_geodata_short9():
    dep = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        crs="EPSG:3857",
    )
    dep13 = dep[dep["insee_dep"] == "13"]
    geo13 = dep13.get_geom()

    bbox = _get_bbox_list(polygon=geo13, update=True, crsPolygon="EPSG:3857")
    assert isinstance(bbox, list)


def test_get_geodata_short_failure():
    data = _get_geodata(dataset_id="test", update=True)
    assert isinstance(data, pd.DataFrame)
    assert not isinstance(data, GeoFrDataFrame)

    with pytest.raises(RuntimeError):
        get_geodata(dataset_id="test", update=True)


if __name__ == "__main__":
    # test_find_wfs_closest_match()
    # test_get_geodata_with_backup()
    test_get_geodata_short()
    # test_get_geodata_short2()
    # test_get_geodata_short3()
    # test_get_geodata_short4()
    # test_get_geodata_short5()
    # test_get_geodata_short5b()
    # test_get_geodata_short6()
    # test_get_geodata_short7()
    # test_get_geodata_short8()
    # test_get_geodata_short9()
    # test_get_geodata_short_failure()
