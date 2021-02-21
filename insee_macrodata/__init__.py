# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 00:53:10 2020

@author: eurhope
"""


from .get_idbank_list import get_idbank_list
from .get_dataset_list import get_dataset_list
from .get_geo_list import get_geo_list

from .get_insee_idbank import get_insee_idbank
from .get_insee_dataset import get_insee_dataset

from .get_column_title import get_column_title
from .split_title import split_title
from .search_insee import search_insee
from ._clean_insee_folder import _clean_insee_folder

# =============================================================================
# to be deleted at the end
# =============================================================================
from ._get_insee import _get_insee
from ._get_dataset_dimension import _get_dataset_dimension
from ._get_dimension_values import _get_dimension_values
from ._download_idbank_list import _download_idbank_list
from ._get_dataset_metadata import _get_dataset_metadata
from ._create_insee_folder import _create_insee_folder
from ._get_idbank_internal_data import _get_idbank_internal_data
from ._get_token import _get_token
from ._request_insee import _request_insee