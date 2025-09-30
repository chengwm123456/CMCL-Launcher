# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import *
from urllib.parse import urlparse, urlunparse

import requests

# from curl_cffi import requests

from .CMCLMirrorMappings import GetMirrorSourceMappings, GetMirrorSourceUrl


def GetVersionsByMojangAPI(returns: str = "RETURN_DATA") -> Union[str, dict, list]:
    version_url = GetMirrorSourceMappings("launchermeta.mojang.com")
    versions_response = requests.get(f"https://{version_url}/mc/game/version_manifest.json")
    versions_data = versions_response.json()
    versions_json = versions_data
    versions = [version["id"] for version in versions_data["versions"]]
    
    latest_version_data = {}
    
    match returns:
        case "RETURN_LATEST":
            return versions_data["latest"]["release"]
        case "RETURN_LATEST_DATA":
            latest_version = versions_data["latest"]["release"]
            for v in range(len(versions_data["versions"])):
                ver = versions_data["versions"][v]
                if ver["id"] == latest_version:
                    latest_version_url = ver["url"]
                    break
            else:
                latest_version_url = versions_data["versions"][0]["url"]
            latest_version_url = GetMirrorSourceUrl(latest_version_url)
            latest_version_response = requests.get(latest_version_url)
            return latest_version_response.json()
        case "RETURN_JSON":
            return versions_json
        case "RETURN_DATA":
            return versions
        case _:
            return versions


def GetVersionsByIterDirectory(minecraft_path: Optional[Union[str, Path, os.PathLike]] = None) -> Optional[Union[list]]:
    if minecraft_path is None:
        minecraft_path = "."
    minecraft_path = Path(minecraft_path)
    versions = []
    if Path(Path(minecraft_path) / "assets").exists() and Path(
            Path(minecraft_path) / "versions").exists():
        for i in os.listdir(minecraft_path / "versions"):
            if Path(minecraft_path / "versions" / i).is_dir():
                j = os.listdir(minecraft_path / "versions" / i)
                if f"{i}.json" in j:
                    versions.append((i, Path(minecraft_path / "versions" / i)))
        return versions
    return None


def GetMinecraftClientDownloadUrl(version: Optional[str] = None) -> str:
    if not version:
        version = GetVersionsByMojangAPI(returns="RETURN_LATEST")
    response = requests.get(
        f'https://{GetMirrorSourceMappings("launchermeta.mojang.com")}/mc/game/version_manifest.json')
    version_manifest = response.json()
    version_id = version
    version_info = None
    for version in version_manifest['versions']:
        if version['id'] == version_id:
            version_info = version
            break
    client_web_url = requests.get(GetMirrorSourceUrl(version_info["url"]))
    client_info = client_web_url.json()
    client_url = GetMirrorSourceUrl(client_info['downloads']['client']['url'])
    return client_url


def GetMinecraftServerDownloadUrl(version: Optional[str] = None) -> str:
    if not version:
        version = GetVersionsByMojangAPI(returns="RETURN_LATEST_DATA")
    response = requests.get(
        f'https://{GetMirrorSourceMappings("launchermeta.mojang.com")}/mc/game/version_manifest.json')
    version_manifest = response.json()
    version_id = version
    version_info = None
    for version in version_manifest['versions']:
        if version['id'] == version_id:
            version_info = version
            break
    server_web_url = requests.get(GetMirrorSourceUrl(version_info["url"]))
    server_info = server_web_url.json()
    server_url = GetMirrorSourceUrl(server_info['downloads']['server']['url'])
    return server_url
