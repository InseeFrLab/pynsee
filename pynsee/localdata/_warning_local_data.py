# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _warning_local_data():
    logger.info(
        "This function renders only package's internal data, "
        "it might not be the most up-to-date.\n"
        "Have a look at api.insee.fr !"
    )
