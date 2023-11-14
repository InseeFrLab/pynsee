# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import base64
import os
import logging
import re
import requests

from functools import lru_cache

import pynsee


logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _get_token_from_insee(insee_key: str, insee_secret: str):
    ''' Return the token from the key and secret '''
    string_key = "{}:{}".format(insee_key, insee_secret)
    string_key_encoded = string_key.encode("utf-8")
    string = base64.b64encode(string_key_encoded).decode("utf-8")

    headers = {
        "Authorization": "Basic {}".format(string),
    }

    data = {"grant_type": "client_credentials"}

    proxies = {
        "http": os.environ.get("http_proxy", pynsee.get_config("http_proxy")),
        "https": os.environ.get(
            "https_proxy", pynsee.get_config("https_proxy"))
    }

    try:
        response = requests.post(
            "https://api.insee.fr/token",
            headers=headers,
            proxies=proxies,
            data=data,
            verify=True,
        )
    except ConnectionError:
        logger.critical("Connection to insee.fr failed !")

    content = response.content.decode("utf-8")
    content_splitted = content.split(",")
    list_access_token = [("access_token" in string) for string in content_splitted]
    selected_content = [x for x, y in zip(content_splitted, list_access_token) if y]
    selected_content = selected_content[0]

    token = re.sub(':|"|}|{|access_token', "", selected_content)

    logger.debug(f"Obtained token: {token}")

    return token
