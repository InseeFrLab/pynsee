# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import appdirs
import os


def _clean_insee_folder():

    local_appdata_folder = appdirs.user_cache_dir()
    insee_folder = local_appdata_folder + '/pynsee' + '/pynsee'

    # delete all files in the folder
    if os.path.exists(insee_folder):
        list_file_insee = os.listdir(insee_folder)
        # exclude directories
        list_file_insee = [file for file in list_file_insee if os.path.isfile(
            os.path.join(insee_folder, file))]

        if len(list_file_insee) > 0:
            for f in list_file_insee:
                os.remove(insee_folder + '/' + f)
