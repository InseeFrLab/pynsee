import pandas as pd
import difflib
import logging

from pynsee.download._get_value_label import _get_value_label
from pynsee.download._get_dict_data_source import _get_dict_data_source
from pynsee.utils._move_col_after import _move_col_before

logger = logging.getLogger(__name__)


def get_column_metadata(id):
    """Get metadata about an insee.fr file

    Returns:
        Returns the request dataframe as a pandas object

    Examples:
        >>> from pynsee.download import get_column_metadata
        >>> rp_logement_metadata = get_column_metadata("RP_LOGEMENT_2016")

    """
    dict_data_source = _get_dict_data_source()

    list_keys_with_metadata = [
        d
        for d in dict_data_source
        if ("val_col" in dict_data_source[d])
        or ("label_col" in dict_data_source[d])
    ]

    id = id.upper()
    id_used = id

    if id not in dict_data_source:
        suggestions = difflib.get_close_matches(
            id, list_keys_with_metadata, n=1, cutoff=0.8
        )

        if len(suggestions) > 0:
            id_used = suggestions[0]
            if not id == id_used:
                logger.warning(
                    f"Metadata for {id} has not been found, metadata for "
                    f"{id_used} is provided instead"
                )

    if id_used in dict_data_source:
        dict_data = dict_data_source[id_used]

        if "label_col" in dict_data:
            labels = pd.DataFrame(dict_data["label_col"], index=[0]).T
            labels["column"] = labels.index
            labels.columns = ["column_label_fr", "column"]
            labels = _move_col_before(labels, "column", "column_label_fr")
            labels = labels.reset_index(drop=True)
        else:
            logger.warning("Columns labels not found in metadata")
            labels = None

        val_col = _get_value_label(id_used)

        if val_col is not None:
            list_val_col = []

            for k in val_col:
                val_col_df = pd.DataFrame(val_col[k], index=[0]).T
                val_col_df[k] = val_col_df.index
                val_col_df.columns = ["value" + "_label_fr", "value"]
                val_col_df["value"] = val_col_df["value"].astype(str)
                val_col_df["column"] = k
                list_val_col += [val_col_df]

            if len(list_val_col) > 0:
                concat_list = pd.concat(list_val_col).reset_index(drop=True)
                labels = labels.merge(concat_list, on=["column"], how="left")
                labels = labels[
                    ["column", "value", "value_label_fr", "column_label_fr"]
                ]
                logger.info(
                    "Column-specific metadata has been found for this file"
                )

    else:
        raise ValueError(
            "id not found in file list, please check metadata "
            "from get_file_list"
        )

    return labels
