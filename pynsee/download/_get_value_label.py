from pynsee.download._get_dict_data_source import _get_dict_data_source


def _get_value_label(id):
    dict_data_source = _get_dict_data_source()
    val_col = None

    if id in dict_data_source.keys():
        dict_data = dict_data_source[id]

        if "val_col" in dict_data.keys():
            val_col = dict_data["val_col"]

    return val_col
