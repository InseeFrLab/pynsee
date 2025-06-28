# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

import pandas as pd
import pytest
from geopandas import GeoSeries
from requests import RequestException
from shapely.geometry import Polygon, MultiPolygon, MultiPoint, Point

from pynsee.geodata import GeoFrDataFrame
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


def test_get_geodata_dep_polygon_crs_4326():
    # run this test before those that use `transform_overseas` to avoid
    # downloading departments multiple times
    dep29 = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        update=True,
        crs="EPSG:4326",
    )

    dep29 = dep29[dep29["code_insee"] == "29"]

    assert isinstance(dep29, GeoFrDataFrame)
    geo29 = dep29.geometry
    assert all(isinstance(p, (MultiPolygon, Polygon)) for p in geo29)

    # query with polygon and non-default crs
    com29 = _get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
        polygon=geo29.union_all(),
        crs_polygon="EPSG:4326",
        update=True,
    )
    assert com29.insee_com.str.startswith("29").any()

    # query with polygon and non-default crs
    com29 = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
        constrain_area=dep29,
        update=True,
    )
    assert com29.insee_com.str.startswith("29").any()


def test_get_geodata_dep_crs_3857():
    # run this test before those that use `transform_overseas` to avoid
    # downloading departments multiple times
    dep29 = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        update=True,
        crs="EPSG:3857",
    )

    dep29 = dep29[dep29["code_insee"] == "29"].to_crs("EPSG:4121")

    assert isinstance(dep29, GeoFrDataFrame)

    # test conversion from non default crs
    com29 = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
        update=True,
        constrain_area=dep29,
    )
    assert com29.insee_com.str.startswith("29").any()


def test_get_geodata_empty():
    square = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]

    poly_bbox = Polygon([[p.x, p.y] for p in square])

    with pytest.warns(RuntimeWarning):
        gdf = _get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
            polygon=poly_bbox,
            update=True,
        )

        assert gdf.empty

    df = get_geodata_list(update=True)
    assert isinstance(df, pd.DataFrame)


def test_get_geodata_overseas():
    chflieu = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:chef_lieu_de_commune",
        update=True,
    )

    assert isinstance(chflieu, GeoFrDataFrame)
    assert all(p.geom_type == "Point" for p in chflieu.geometry)

    with pytest.warns(DeprecationWarning):
        geo = chflieu.get_geom()
        assert isinstance(geo, MultiPoint)

    geo_chflieu = chflieu.transform_overseas().zoom().geometry
    assert isinstance(geo_chflieu, GeoSeries)
    assert all(p.geom_type == "Point" for p in geo_chflieu)


def test_get_geodata_communes():
    com = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune", update=True
    )
    assert isinstance(com, GeoFrDataFrame)
    assert len(com) > 30000
    assert all(isinstance(p, (Polygon, MultiPolygon)) for p in com.geometry)


def test_get_geodata_com_overseas():
    com = get_geodata(dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune")
    ovdep = com.transform_overseas().zoom()
    assert isinstance(ovdep, GeoFrDataFrame)
    assert all(isinstance(p, (Polygon, MultiPolygon)) for p in ovdep.geometry)


def test_get_geodata_epci():
    # test _add_insee_dep_from_geodata
    epci = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:epci", update=True
    )
    assert isinstance(epci, GeoFrDataFrame)
    epcit = epci.transform_overseas().zoom()
    assert isinstance(epcit, GeoFrDataFrame)
    assert all(isinstance(p, (Polygon, MultiPolygon)) for p in epcit.geometry)


def test_get_geodata_region():
    # test _add_insee_dep_region
    reg = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:region", update=True
    )
    assert isinstance(reg, GeoFrDataFrame)
    regt = reg.transform_overseas().zoom()
    assert isinstance(regt, GeoFrDataFrame)
    assert all(isinstance(p, (Polygon, MultiPolygon)) for p in regt.geometry)


def test_get_geodata_bbox_list():
    dep = get_geodata(
        dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
        crs="EPSG:4326",
    )

    dep13 = dep[dep["code_insee"] == "13"]

    geo13 = dep13.union_all()

    bbox = _get_bbox_list(polygon=geo13, update=True, crsPolygon="EPSG:4326")
    assert isinstance(bbox, list)
    bbox = _get_bbox_list(polygon=geo13)
    assert isinstance(bbox, list)

    # change crs
    dep13 = dep13.to_crs("EPSG:3857")
    geo13 = dep13.union_all()

    bbox = _get_bbox_list(polygon=geo13, update=True, crsPolygon="EPSG:3857")
    assert isinstance(bbox, list)


def test_get_geodata_short_failure():
    with pytest.warns(RuntimeWarning):
        data = _get_geodata(dataset_id="test", update=True)
        assert isinstance(data, GeoFrDataFrame)
        assert data.empty

    with pytest.raises(RequestException):
        get_geodata(dataset_id="test", update=True)

    with pytest.raises(RequestException):
        _get_geodata(dataset_id="test", ignore_error=False, update=True)


if __name__ == "__main__":
    test_find_wfs_closest_match()
    test_get_geodata_with_backup()
    test_get_geodata_dep_polygon_crs_4326()
    test_get_geodata_dep_crs_3857()
    test_get_geodata_empty()
    test_get_geodata_overseas()
    test_get_geodata_communes()
    test_get_geodata_com_overseas()
    test_get_geodata_epci()
    test_get_geodata_region()
    test_get_geodata_bbox_list()
    test_get_geodata_with_backup()
    test_get_geodata_short_failure()
