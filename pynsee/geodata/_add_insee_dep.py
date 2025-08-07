from tqdm import trange
from pandas.api.types import CategoricalDtype
import numpy as np
import pandas as pd

from ._get_geodata_with_backup import _get_geodata_with_backup


def _add_insee_dep(gdf):
    gdf = gdf.reset_index(drop=True)

    # option 1 : get insee_dep from id_com colum
    gdf = _add_insee_dep_from_id_com(gdf)

    # option 2 : get insee_dep for regions
    if "insee_dep" not in gdf:
        gdf = _add_insee_dep_region(gdf)

        # option 3 : get insee_dep from get_geodata  and polygon intersection
        if "insee_dep" not in gdf:
            gdf = _add_insee_dep_from_geodata(gdf)

    if "insee_dep_geometry" not in gdf:
        raise ValueError("Could not get department geometries.")

    return gdf


def _add_insee_dep_from_id_com(gdf):
    # add insee_dep column

    if "cleabs" in gdf.columns:
        if all(gdf.cleabs.str.match("^COMMUNE")):
            if "code_insee_du_departement" not in gdf.columns:

                dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:commune"
                com = _get_geodata_with_backup(dataset_id).to_crs("EPSG:3857")

                com = com[["cleabs", "code_insee_du_departement"]]
                gdf = gdf.merge(com, on="cleabs", how="left")

        if "code_insee_du_departement" in gdf.columns:
            # get departments and add the geometry
            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
            dep = _get_geodata_with_backup(dataset_id).to_crs("EPSG:3857")

            dep = dep[["code_insee", "geometry"]]
            dep.rename(
                columns={
                    "geometry": "insee_dep_geometry",
                    "code_insee": "code_insee_du_departement",
                },
                inplace=True
            )

            gdf = gdf.merge(
                dep, on="code_insee_du_departement", how="left"
            ).assign(
                insee_dep_geometry=lambda x: np.where(
                    x["code_insee_du_departement"] == "NR",
                    x["geometry"],
                    x["insee_dep_geometry"],
                )
            )

    return gdf


def _add_insee_dep_region(gdf):
    try:
        if "cleabs" in gdf.columns and all(gdf.cleabs.str.match("^REGION")):
            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"

            # get departments, keep only one for each region
            dep = (
                _get_geodata_with_backup(dataset_id)
                .drop_duplicates(
                    subset="code_insee_de_la_region", keep="first"
                )
                .to_crs("EPSG:3857")
            )

            dep = dep[["code_insee", "code_insee_de_la_region", "geometry"]]
            dep.rename(
                columns={
                    "geometry": "insee_dep_geometry",
                },
                inplace=True
            )

            gdf = gdf.merge(dep, on="insee_reg", how="left")
    except Exception:
        pass

    return gdf


def _add_insee_dep_from_geodata(gdf):
    try:
        if "insee_dep_geometry" not in gdf.columns:
            gdf = gdf.reset_index(drop=True)

            list_dep = []
            list_dep_geo = []

            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
            dep_list = _get_geodata_with_backup(dataset_id).to_crs("EPSG:3857")

            com = _get_geodata_with_backup(
                "ADMINEXPRESS-COG-CARTO.LATEST:commune"
            ).to_crs("EPSG:3857")
            stpm = com.loc[lambda x: x["code_insee"].str.contains("^975")]
            stpmGeo = stpm.geometry.union_all()

            dep_list = pd.concat(
                [
                    pd.DataFrame(
                        {"code_insee": "NR", "geometry": stpmGeo}, index=[0]
                    ),
                    dep_list,
                ]
            )

            list_ovdep = ["971", "972", "974", "NR", "973", "976"]
            list_other_dep = [
                d for d in dep_list.code_insee if d not in list_ovdep
            ]
            dep_order = list_ovdep + list_other_dep

            dep_list["code_insee"] = dep_list["code_insee"].astype(
                CategoricalDtype(categories=dep_order, ordered=True)
            )

            dep_list = dep_list.sort_values(["code_insee"]).reset_index(
                drop=True
            )

            for i in trange(len(gdf.index), desc="Finding departement"):
                geo = gdf.loc[i, "geometry"]
                dep = None
                depgeo = None

                try:
                    for j in dep_list.index:
                        depgeo = dep_list.loc[j, "geometry"]
                        if geo.intersects(depgeo):

                            dep = dep_list.loc[j, "code_insee"]

                            break
                        else:
                            depgeo = None
                except Exception:
                    pass

                list_dep += [dep]
                list_dep_geo += [depgeo]

            gdf["code_insee_du_departement"] = list_dep
            gdf["insee_dep_geometry"] = list_dep_geo
    except Exception:
        pass

    return gdf
