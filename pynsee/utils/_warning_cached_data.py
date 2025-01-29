# -*- coding: utf-8 -*-
from functools import lru_cache

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _warning_cached_data(file):
    logger.info(
        f"Previously saved data has been used:\n{file}\n"
        "Set update=True to get the most up-to-date data"
    )
