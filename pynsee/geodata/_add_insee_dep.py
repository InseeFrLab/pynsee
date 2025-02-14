from tqdm import trange
from pandas.api.types import CategoricalDtype

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
    if "insee_com" in gdf.columns:
        gdf.loc[:, "insee_dep"] = [
            v[:3] if v.startswith("97") else v[:2]
            for v in gdf.insee_com.values
        ]
    elif "id_com" in gdf.columns:
        try:
            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:commune"
            com = _get_geodata_with_backup(dataset_id).to_crs("EPSG:3857")

            com = com[["id", "insee_dep"]]
            com = com.rename(columns={"id": "id_com"})
            gdf = gdf.merge(com, on="id_com", how="left")
        except Exception:
            return gdf

    # get departments and add the geometry
    try:
        dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
        dep = _get_geodata_with_backup(dataset_id).to_crs("EPSG:3857")

        dep = dep[["insee_dep", "geometry"]]
        dep = dep.rename(columns={"geometry": "insee_dep_geometry"})

        gdf = gdf.merge(dep, on="insee_dep", how="left")
    except Exception:
        pass

    return gdf


def _add_insee_dep_region(gdf):
    try:
        if "id" in gdf.columns and all(gdf.id.str.match("^REGION")):
            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"

            # get departments, keep only one for each region
            dep = (
                _get_geodata_with_backup(dataset_id)
                .drop_duplicates(subset="insee_reg", keep="first")
                .to_crs("EPSG:3857")
            )

            dep = dep[["insee_dep", "insee_reg", "geometry"]]
            dep = dep.rename(columns={"geometry": "insee_dep_geometry"})
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

            list_ovdep = ["971", "972", "974", "973", "976"]
            list_other_dep = [
                d for d in dep_list.insee_dep if d not in list_ovdep
            ]
            dep_order = list_ovdep + list_other_dep

            dep_list["insee_dep"] = dep_list["insee_dep"].astype(
                CategoricalDtype(categories=dep_order, ordered=True)
            )

            dep_list = dep_list.sort_values(["insee_dep"]).reset_index(
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
                            dep = dep_list.loc[j, "insee_dep"]
                            break
                        else:
                            depgeo = None
                except Exception:
                    pass

                list_dep += [dep]
                list_dep_geo += [depgeo]

            gdf["insee_dep"] = list_dep
            gdf["insee_dep_geometry"] = list_dep_geo
    except Exception:
        pass

    return gdf
