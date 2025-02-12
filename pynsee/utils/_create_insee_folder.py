# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import os
import platformdirs

from pynsee.utils._get_temp_dir import _get_temp_dir
from pynsee.utils._hash import _hash

import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _create_insee_folder():

    try:

        # find local folder
        local_appdata_folder = platformdirs.user_cache_dir(
            "pynsee", ensure_exists=True
        )

        # create insee folder
        insee_folder = os.path.join(local_appdata_folder, "pynsee")
        os.makedirs(insee_folder, exist_ok=True)

        # test if saving a file is possible
        test_file = os.path.join(insee_folder, _hash("test_file"))
        with open(test_file, "w") as f:
            f.write("")
        # testing requires restricted rights on the machine

    except Exception:
        # if error temporary folder is returned
        insee_folder = _get_temp_dir()
        logger.warning(
            "pynsee folder could not be created in the appdata folder. "
            "Therefore, cache will only be handled in the current python "
            "session and you ARE responsible to clean the following temporary "
            "folder (at " + insee_folder + ") once you've finished!\n"
        )

    return insee_folder
