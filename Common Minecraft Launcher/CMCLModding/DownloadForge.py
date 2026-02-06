# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from zipfile import ZipFile

from .GetFabric import GetDownloadUrlBase
from CMCLCore.CMCLDefines.Downloader import Downloader
from CMCLCore.CMCLGameDownloading import DownloadMinecraft, DownloadLibraryFile


def DownloadNeoForgeJSON(game, loader, minecraft_path, **options):
    Downloader(f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{loader}/neoforge-{loader}-installer.jar",
               None, minecraft_path, options.get("max_workers", 8),
               options.get("chunk_size", 1024 * 1024 * 8)).downloadFile()
    with ZipFile(minecraft_path / f"neoforge-{loader}-installer.jar") as zip_file:
        zip_file.extract("version.json", minecraft_path / "versions" / f"neoforge-{loader}-{game}")
        (minecraft_path / "versions" / f"neoforge-{loader}-{game}" / "versions.json").rename(
            minecraft_path / "versions" / f"neoforge-{loader}-{game}" / f"neoforge-{loader}-{game}.json")
    (minecraft_path / f"neoforge-{loader}-installer.jar").unlink(missing_ok=True)


def DownloadNeoForgeLibraries(json_info, minecraft_path):
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


def DownloadNeoForgeFull(game, loader, minecraft_path, vanilla_download=True, **options):
    (minecraft_path / "versions" / f"neoforge-{loader}").mkdir(parents=True, exist_ok=True)
    DownloadNeoForgeJSON(game, loader, minecraft_path, **options)
    json_file = minecraft_path / "versions" / f"neoforge-{loader}-{game}" / f"neoforge-{loader}-{game}.json"
    json_info = json.loads(Path(json_file).read_text(encoding="utf-8"))
    DownloadNeoForgeLibraries(json_info, minecraft_path)
    if vanilla_download:
        DownloadMinecraft(minecraft_path, game, **options)
