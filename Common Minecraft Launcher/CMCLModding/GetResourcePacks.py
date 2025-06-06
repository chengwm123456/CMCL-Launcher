# -*- coding: utf-8 -*-
import requests


def GetResourcePacks(limit=10, offset=0):
    response = requests.get("https://api.modrinth.com/v2/search",
                            params={"facets": "[[\"project_type: resourcepack\"]]", "limit": limit, "offset": offset})
    res_json = response.json()
    return res_json
