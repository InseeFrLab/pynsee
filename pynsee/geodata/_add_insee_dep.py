from tqdm import trange
from pandas.api.types import CategoricalDtype

from pynsee.geodata._get_geodata import _get_geodata
from pynsee.geodata._get_geodata_with_backup import _get_geodata_with_backup

def _add_insee_dep(df):

    df = df.reset_index(drop=True)

    # option 1 : get insee_dep from id_com colum
    df = _add_insee_dep_from_id_com(df)

    # option 2 : get insee_dep for regions
    df = _add_insee_dep_region(df)

    # option 3 : get insee_dep from get_geodata  and polygon intersection
    df = _add_insee_dep_from_geodata(df)

    return df


def _add_insee_dep_region(df):

    try:
        if "insee_dep_geometry" not in df.columns:
            if "id" in df.columns:
                if all(df.id.str.contains("^REGION")):
                    dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
                    dep = _get_geodata_with_backup(dataset_id)
                        
                    dep = dep[["insee_dep", "insee_reg", "geometry"]]
                    dep = dep.rename(columns={"geometry": "insee_dep_geometry"})
                    df = df.merge(dep, on="insee_reg", how="left")

    except Exception as e:
        #print(e)
        pass

    return df


def _add_insee_dep_from_id_com(df):

    try:

        if ("id_com" in df.columns) and ("insee_dep_geometry" not in df.columns):
            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:commune"
            com = _get_geodata_with_backup(dataset_id)
                     
            com = com[["id", "insee_dep"]]
            com = com.rename(columns={"id": "id_com"})
            df = df.merge(com, on="id_com", how="left")

            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
            dep = _get_geodata_with_backup(dataset_id)
            
            dep = dep[["insee_dep", "geometry"]]
            dep = dep.rename(columns={"geometry": "insee_dep_geometry"})

            df = df.merge(dep, on="insee_dep", how="left")
    except Exception as e:
        #print(e)
        pass

    return df


def _add_insee_dep_from_geodata(df):

    try:
        if "insee_dep_geometry" not in df.columns:

            df = df.reset_index(drop=True)

            list_dep = []
            list_dep_geo = []
            
            dataset_id = "ADMINEXPRESS-COG-CARTO.LATEST:departement"
            dep_list = _get_geodata_with_backup(dataset_id)
            
            list_ovdep = ["971", "972", "974", "973", "976"]
            list_other_dep = [d for d in dep_list.insee_dep if d not in list_ovdep]
            dep_order = list_ovdep + list_other_dep

            dep_list["insee_dep"] = dep_list["insee_dep"].astype(
                CategoricalDtype(categories=dep_order, ordered=True)
            )

            dep_list = dep_list.sort_values(["insee_dep"]).reset_index(drop=True)

            for i in trange(len(df.index), desc="Finding departement"):
                geo = df.loc[i, "geometry"]
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
                except:
                    pass

                list_dep += [dep]
                list_dep_geo += [depgeo]

            df["insee_dep"] = list_dep
            df["insee_dep_geometry"] = list_dep_geo
    except Exception as e:
        #print(e)
        pass

    return df
