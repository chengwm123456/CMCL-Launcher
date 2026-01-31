# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from zipfile import ZipFile

from .GetFabric import GetDownloadUrlBase
from CMCLCore.CMCLDefines.Downloader import Downloader
from CMCLCore.CMCLGameDownloading import DownloadMinecraft, DownloadLibraryFile


def DownloadFabric(game, loader, path, target_path):
    target_path = Path(target_path)
    base_url = GetDownloadUrlBase(game, loader)
    base_url += "/" + path.strip("/")
    downloader = Downloader(base_url, "", target_path)
    downloader.downloadFile()


def DownloadFabricZip(game, loader, target_path):
    DownloadFabric(game, loader, "/profile/zip", Path(target_path))


def DownloadFabricLibraries(json_info, minecraft_path):
    libraries_file_data = json_info["libraries"]
    for i in range(0, len(libraries_file_data)):
        data = libraries_file_data[i]
        name_of_file = data["name"].split(":")
        path_of_file = Path(name_of_file[0].replace(".", "/")) / name_of_file[1] / name_of_file[2]
        file_name = "-".join(name_of_file[1:]) + ".jar"
        full_path = path_of_file / file_name
        libraries_dir_path = Path(minecraft_path / "libraries")
        path = Path(libraries_dir_path / full_path)
        url = data["url"]
        full_url = str(full_path).replace(os.sep, "/")
        url = url.rstrip("/") + "/" + full_url.lstrip("/")
        if not Path(path).exists():
            DownloadLibraryFile(url, path)


def DownloadFabricFull(game, loader, minecraft_path, vanilla_download=True):
    versions_path = Path(minecraft_path) / "versions"
    if not (versions_path / f"fabric-loader-{loader}-{game}").exists():
        DownloadFabricZip(game, loader, versions_path)
        zip_path = versions_path / f"fabric-loader-{loader}-{game}.zip"
        zip_file = ZipFile(zip_path)
        zip_file.extractall(versions_path)
        zip_file.close()
        zip_path.unlink(missing_ok=True)
    jar_file = versions_path / f"fabric-loader-{loader}-{game}" / f"fabric-loader-{loader}-{game}.jar"
    if (versions_path / game / f"{game}.jar").exists():
        jar_file.unlink(missing_ok=True)
        jar_file.symlink_to(versions_path / game / f"{game}.jar")
    json_file = versions_path / f"fabric-loader-{loader}-{game}" / f"fabric-loader-{loader}-{game}.json"
    json_info = json.loads(Path(json_file).read_text(encoding="utf-8"))
    DownloadFabricLibraries(json_info, minecraft_path)
    if vanilla_download:
        DownloadMinecraft(minecraft_path, game)
