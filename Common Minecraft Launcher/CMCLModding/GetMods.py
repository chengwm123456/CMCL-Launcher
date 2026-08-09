# -*- coding: utf-8 -*-
import requests


def GetMods(limit=10, offset=0):
    response = requests.get("https://api.modrinth.com/v2/search",
                            params={"facets": "[[\"project_type: mod\"]]", "limit": limit, "offset": offset},
                            headers={"User-Agent": "Common Minecraft Launcher (CMCL)"})
    res_json = response.json()
    return res_json


def SearchMods(query, limit=10, offset=0):
    response = requests.get("https://api.modrinth.com/v2/search",
                            params={"query": query, "facets": "[[\"project_type: mod\"]]", "limit": limit,
                                    "offset": offset},
                            headers={"User-Agent": "CMCL"})
    res_json = response.json()
    return res_json


def ListModVersions(name=""):
    hit = requests.get("https://api.modrinth.com/v2/search",
                       params={"facets": "[[\"project_type: mod\"]]", "limit": 1, "query": name},
                       headers={"User-Agent": "CMCL"}).json()["hits"][0]
    mod_id = hit["id"]
    response = requests.get(f"https://api.modrinth.com/v2/project/{mod_id}/version").json()
    return response


def GetOneMod(id_or_slug=""):
    response = requests.get(f"https://api.modrinth.com/v2/project/{id_or_slug}",
                            headers={"User-Agent": "CMCL"})
    res_json = response.json()
    return res_json


# Extend functionalities that allows you to search more variants of projects on Modrinth.
def GetProjects(limit=10, offset=0, project_type="mod"):
    response = requests.get("https://api.modrinth.com/v2/search",
                            params={"facets": f"[[\"project_type: {project_type}\"]]", "limit": limit,
                                    "offset": offset},
                            headers={"User-Agent": "CMCL"})
    res_json = response.json()
    return res_json


def ListModVersions(name="", project_type="mod"):
    hit = requests.get("https://api.modrinth.com/v2/search",
                       params={"facets": f"[[\"project_type: {project_type}\"]]", "limit": 1, "query": name},
                       headers={"User-Agent": "CMCL"}).json()["hits"][0]
    mod_id = hit["id"]
    response = requests.get(f"https://api.modrinth.com/v2/project/{mod_id}/version").json()
    return response


def GetOneMod(id_or_slug=""):
    response = requests.get(f"https://api.modrinth.com/v2/project/{id_or_slug}")
    res_json = response.json()
    return res_json
