# -*- coding: utf-8 -*-
from .GetMods import ListModVersions
from CMCLCore.CMCLDefines.Downloader import Downloader


def DownloadMod(mod_name, mod_version, target_path):
    mod_versions = ListModVersions(mod_name)
    mod_files = None
    for version in mod_versions:
        if version["version_number"] == mod_version or version["name"] == mod_version:
            mod_files = version["files"]
            break
    if not mod_files:
        return
    downloaders = []
    for file in mod_files:
        downloader = Downloader(file["url"], file["filename"], target_path)
        downloader.downloadFile()
        downloaders.append(downloader)
