# -*- coding: utf-8 -*-
import requests
from pathlib import Path

from .GetMods import ListModVersions


def DownloadMod(mod_name, mod_version, target_path):
    mod_versions = ListModVersions(mod_name)
    mod_files = None
    for version in mod_versions:
        if version["version_number"] == mod_version or version["name"] == mod_version:
            mod_files = version["files"]
            break
    if not mod_files:
        return
    Path(target_path).mkdir(exist_ok=True)
    for file in mod_files:
        response = requests.get(file["url"], headers={"User-Agent": "CMCL"})
        (Path(target_path) / file["filename"]).write_bytes(response.content)
        # downloader = Downloader(file["url"], file["filename"], target_path)
        # downloader.downloadFile()
        # downloaders.append(downloader)
