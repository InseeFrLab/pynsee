# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import requests
import re
import base64
import os

from functools import lru_cache


@lru_cache(maxsize=None)
def _get_token_from_insee(insee_key, insee_secret):

    string_key = "{}:{}".format(insee_key, insee_secret)
    string_key_encoded = string_key.encode("utf-8")
    string = base64.b64encode(string_key_encoded).decode("utf-8")

    headers = {
        "Authorization": "Basic {}".format(string),
    }

    data = {"grant_type": "client_credentials"}

    try:
        proxies = {"http": os.environ["http_proxy"], "https": os.environ["http_proxy"]}
    except:
        proxies = {"http": "", "https": ""}

    try:
        response = requests.post(
            "https://api.insee.fr/token",
            headers=headers,
            proxies=proxies,
            data=data,
            verify=True,
        )
    except ConnectionError:
        print("\n!!! Connection to insee.fr failed !!!\n")

    content = response.content.decode("utf-8")
    content_splitted = content.split(",")
    list_access_token = [("access_token" in string) for string in content_splitted]
    selected_content = [x for x, y in zip(content_splitted, list_access_token) if y]
    selected_content = selected_content[0]

    token = re.sub(':|"|}|{|access_token', "", selected_content)

    return token
