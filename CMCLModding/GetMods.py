# -*- coding: utf-8 -*-
import requests


def GetMods(limit=10, offset=0):
    response = requests.get("https://api.modrinth.com/v2/search",
                            params={"facets": "[[\"project_type: mod\"]]", "limit": limit, "offset": offset})
    res_json = response.json()
    return res_json


def ListModVersions(name=""):
    hit = requests.get("https://api.modrinth.com/v2/search",
                       params={"facets": "[[\"project_type: mod\"]]", "limit": 1, "query": name}).json()["hits"][0]
    slug = hit["slug"]
    response = requests.get(f"https://api.modrinth.com/v2/project/{slug}/version").json()
    return response
