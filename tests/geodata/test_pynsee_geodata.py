# -*- coding: utf-8 -*-
# Copyright : INSEE, 2022

from unittest import TestCase
import pandas as pd
import unittest

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


class TestFunction(TestCase):

    def test_find_wfs_closest_match(self):
        self.assertTrue(isinstance(_find_wfs_closest_match(), str))

    def test_get_geodata_with_backup(self):
        gdf = _get_geodata_with_backup("ADMINEXPRESS-COG.LATEST:departement")
        self.assertTrue(isinstance(gdf, GeoFrDataFrame))

    def test_get_geodata_short(self):
        square = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]

        poly_bbox = Polygon([[p.x, p.y] for p in square])
        df = _get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
            polygon=poly_bbox,
            update=True,
        )
        self.assertTrue(isinstance(df, GeoFrDataFrame))

        df = get_geodata_list(update=True)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_geodata_short2(self):
        chflieu = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:chflieu_commune",
            update=True,
        )

        self.assertTrue(isinstance(chflieu, GeoFrDataFrame))
        self.assertTrue(all(p.geom_type == "Point" for p in chflieu.geometry))

        with self.assertWarns(Warning):
            geo = chflieu.get_geom()
            self.assertTrue(isinstance(geo, GeoSeries))

        geo_chflieu = chflieu.translate().zoom().geometry
        self.assertTrue(isinstance(geo_chflieu, GeoSeries))
        self.assertTrue(all(p.geom_type == "Point" for p in geo_chflieu))

    def test_get_geodata_short3(self):
        com = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune", update=True
        )
        self.assertTrue(isinstance(com, GeoFrDataFrame))
        self.assertTrue(
            all(isinstance(p, (Polygon, MultiPolygon)) for p in com.geometry)
        )

    def test_get_geodata_short4(self):
        # query with polygon and crs 4326
        dep29 = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
            update=True,
            crs="EPSG:4326",
        )
        dep29 = dep29[dep29["insee_dep"] == "29"]
        self.assertTrue(isinstance(dep29, GeoFrDataFrame))
        geo29 = dep29.geometry
        self.assertTrue(
            all(isinstance(p, (MultiPolygon, Polygon)) for p in geo29)
        )

        com29 = _get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
            update=True,
            polygon=geo29,
            crsPolygon="EPSG:4326",
        )
        self.assertTrue(isinstance(com29, GeoFrDataFrame))

    def test_get_geodata_short5(self):

        # query with polygon and crs 3857
        dep29 = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
            update=True,
            crs="EPSG:3857",
        )
        dep29 = dep29[dep29["insee_dep"] == "29"]
        self.assertTrue(isinstance(dep29, GeoFrDataFrame))

        geo29 = dep29.get_geom()
        self.assertTrue(isinstance(geo29, MultiPolygon))
        com29 = _get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune",
            update=True,
            polygon=geo29,
            crsPolygon="EPSG:3857",
        )
        self.assertTrue(isinstance(com29, GeoFrDataFrame))

    def test_get_geodata_short5b(self):

        com = get_geodata(dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:commune")
        ovdep = com.translate().zoom()
        self.assertTrue(isinstance(ovdep, GeoFrDataFrame))
        geo_ovdep = ovdep.get_geom()
        self.assertTrue(isinstance(geo_ovdep, MultiPolygon))

    def test_get_geodata_short6(self):
        # test _add_insee_dep_from_geodata
        epci = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:epci", update=True
        )
        self.assertTrue(isinstance(epci, GeoFrDataFrame))
        epcit = epci.translate().zoom()
        self.assertTrue(isinstance(epcit, GeoFrDataFrame))
        geo_epcit = epcit.get_geom()
        self.assertTrue(isinstance(geo_epcit, MultiPolygon))

    def test_get_geodata_short7(self):
        # test _add_insee_dep_region
        reg = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:region", update=True
        )
        self.assertTrue(isinstance(reg, GeoFrDataFrame))
        regt = reg.translate().zoom()
        self.assertTrue(isinstance(regt, GeoFrDataFrame))
        geo_regt = regt.get_geom()
        self.assertTrue(isinstance(geo_regt, MultiPolygon))

    def test_get_geodata_short8(self):
        dep = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
            crs="EPSG:4326",
        )
        dep13 = dep[dep["insee_dep"] == "13"]
        geo13 = dep13.get_geom()

        bbox = _get_bbox_list(
            polygon=geo13, update=True, crsPolygon="EPSG:4326"
        )
        self.assertTrue(isinstance(bbox, list))
        bbox = _get_bbox_list(polygon=geo13)
        self.assertTrue(isinstance(bbox, list))

    def test_get_geodata_short9(self):
        dep = get_geodata(
            dataset_id="ADMINEXPRESS-COG-CARTO.LATEST:departement",
            crs="EPSG:3857",
        )
        dep13 = dep[dep["insee_dep"] == "13"]
        geo13 = dep13.get_geom()

        bbox = _get_bbox_list(
            polygon=geo13, update=True, crsPolygon="EPSG:3857"
        )
        self.assertTrue(isinstance(bbox, list))

    def test_get_geodata_short_failure(self):
        data = _get_geodata(dataset_id="test", update=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(not isinstance(data, GeoFrDataFrame))

        with self.assertRaises(RuntimeError):
            get_geodata(dataset_id="test", update=True)


if __name__ == "__main__":
    unittest.main()
    # python test_pynsee_geodata.py
