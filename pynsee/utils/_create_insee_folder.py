# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from functools import lru_cache
import os
import platformdirs

from pynsee.utils._get_temp_dir import _get_temp_dir
from pynsee.utils._hash import _hash


@lru_cache(maxsize=None)
def _create_insee_folder():

    try:

        # find local folder
        local_appdata_folder = platformdirs.user_cache_dir()
        insee_folder = os.path.join(local_appdata_folder, "pynsee")

        # create insee folder
        if not os.path.exists(insee_folder):
            os.mkdir(insee_folder)

        insee_folder = os.path.join(insee_folder, "pynsee")

        # create insee folder
        if not os.path.exists(insee_folder):
            os.mkdir(insee_folder)

        # test if saving a file is possible
        test_file = os.path.join(insee_folder, _hash("test_file"))
        with open(test_file, "w") as f:
            f.write("")
            f.close()
        # testing requires restricted rights on the machine
    except:
        # if error temporary folder is returned
        insee_folder = _get_temp_dir()
    finally:
        return insee_folder
