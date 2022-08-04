import tempfile


def _import_options(caract: dict, filename: str):
    """Internal to generate a dictionary of options
    required to import files

    Arguments:
        caract {dict} -- Dictionary returned by `download_store_file`
        filename {str} -- Filename of the object that is going to be imported

    Returns:
        dict -- A dictionary listing options to control
         import with `pandas`
    """

    if caract["zip"] is True:
        file_archive = filename
        file_to_import = f"{tempfile.gettempdir()}/{caract['fichier_donnees']}"
    else:
        file_archive = None
        file_to_import = filename

    import_args = {"file": file_to_import}

    if caract["type"] == "csv":
        import_args.update({"delim": caract["separateur"], "col_names": True})
        if "encoding" in list(caract.keys()):
            import_args.update({"locale": caract["encoding"]})
    elif caract["type"] in ["xls", "xlsx"]:
        import_args.update(
            {"path": file_to_import, "skip": caract["premiere_ligne"] - 1}
        )
        if "onglet" in list(caract.keys()):
            import_args.update({"sheet": caract["onglet"]})
        else:
            import_args.update({"sheet": 0})
        if "derniere_ligne" in list(caract.keys()):
            nmax_rows = caract["derniere_ligne"] - caract["premiere_ligne"]
            import_args.update({"n_max": nmax_rows})
        else:
            import_args.update({"n_max": None})

        if "valeurs_manquantes" in list(caract.keys()):
            import_args.update({"na": caract["valeurs_manquantes"]})
        else:
            import_args.update({"na": None})

    if "type_col" in list(caract.keys()):
        list_cols = caract["type_col"]
        for key, value in list_cols.items():
            if value == "character":
                list_cols[key] = "str"
            elif value == "integer":
                list_cols[key] = "int"
            elif value == "number":
                list_cols[key] = "float"
    else:
        list_cols = None

    import_args.update({"dtype": list_cols})
    try:
        encoding = caract["encoding"]
    except:
        encoding = "Nan"
    import_args.update({"encoding": encoding})

    out_dict = {
        "file_archive": file_archive,
        "file_to_import": file_to_import,
        "import_args": import_args,
    }

    return out_dict
