# -*- coding: utf-8 -*-
import os
from pathlib import Path

import requests


# from curl_cffi import requests


def GetVersionByMojangApi(returns="RETURN_DATA"):
    mojang_api_url = "https://launchermeta.mojang.com"
    
    versions_url = f"{mojang_api_url}/mc/game/version_manifest.json"
    versions_response = requests.get(versions_url)
    versions_data = versions_response.json()
    versions_json = versions_data
    versions = [version["id"] for version in versions_data["versions"]]
    
    latest_version = versions_data["latest"]["release"]
    for v in range(len(versions_data["versions"])):
        ver = versions_data["versions"][v]
        if ver["id"] == latest_version:
            latest_version_url = ver["url"]
            break
    else:
        latest_version_url = versions_data["versions"][0]["url"]
    latest_version_response = requests.get(latest_version_url)
    latest_version_data = latest_version_response.json()
    match returns:
        case "RETURN_LATEST":
            return latest_version
        case "RETURN_LATEST_DATA":
            return latest_version_data
        case "RETURN_JSON":
            return versions_json
        case "RETURN_DATA":
            return versions
        case _:
            return versions


def GetVersionByScanDirectory(minecraft_path=None):
    if minecraft_path is None:
        minecraft_path = "."
    minecraft_path = Path(minecraft_path)
    versions = []
    if Path(Path(minecraft_path) / "assets").exists() and Path(
            Path(minecraft_path) / "versions").exists():
        for i in os.listdir(minecraft_path / "versions"):
            j = os.listdir(minecraft_path / "versions" / i)
            if f"{i}.jar" in j:
                versions.append(i)
        return versions
    return "No matched versions"


def GetMinecraftClientDownloadUrl(**kw):
    response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    version_manifest = response.json()
    version_id = kw.get("version", GetVersionByMojangApi(returns="RETURN_LATEST_DATA"))
    version_info = None
    for version in version_manifest['versions']:
        if version['id'] == version_id:
            version_info = version
            break
    client_web_url = requests.get(version_info["url"])
    client_info = client_web_url.json()
    client_url = client_info['downloads']['client']['url']
    return client_url
