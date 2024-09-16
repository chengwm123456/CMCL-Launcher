# -*- coding: utf-8 -*-
import hashlib
import json
import os
from typing import *

from . import GetOperationSystem
from .Downloader import Downloader
from .GetVersion import *


def DownloadVersionJson(version: Union[str, None] = None,
                        minecraft_path: Union[str, Path, os.PathLike, LiteralString] = "."):
    minecraft_path = Path(minecraft_path)
    if version is not None:
        response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
        version_manifest = response.json()
        version_id = version
        version_info = None
        for v in version_manifest['versions']:
            if v['id'] == version_id:
                version_info = v
                break
        json_url = requests.get(version_info["url"])
        json_info = json_url.json()
        path = Path(minecraft_path / "versions" / version,
                    f"{version}.json")
        Path(path).write_text(
            json.dumps(
                json_info,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
    else:
        pass


def _DownloadLibraryFile(url: str, path: Union[str, Path, os.PathLike, LiteralString] = "."):
    path, file_name = Path(*(Path(path).parts[:-1])), Path(Path(path).parts[-1])
    Path(path).mkdir(parents=True, exist_ok=True)
    file_path = Path(path / file_name)
    if not Path(file_path).exists():
        downloader = Downloader(url, file_path)
        downloader.download()


def DownloadAssetIndexFile(minecraft_path: Union[str, Path, os.PathLike, LiteralString] = ".",
                           json_path: Union[str, Path, os.PathLike, LiteralString] = "."):
    minecraft_path = Path(minecraft_path)
    assets_file_data = json.loads(Path(json_path).read_text(encoding="utf-8"))["assetIndex"]
    if not Path(minecraft_path / "assets" / "indexes").exists():
        os.makedirs(Path(minecraft_path / "assets" / "indexes"))
    file_path = Path(minecraft_path / "assets" / "indexes" / f"{assets_file_data['id']}.json")
    if not Path(file_path).exists():
        response = requests.get(assets_file_data["url"])
        assets_info = response.json()
        Path(file_path).write_text(
            json.dumps(
                assets_info,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
    else:
        sha1 = hashlib.sha1(Path(file_path).read_bytes())
        if sha1.hexdigest() != assets_file_data["sha1"]:
            response = requests.get(assets_file_data["url"])
            assets_info = response.json()
            Path(file_path).write_text(
                json.dumps(
                    assets_info,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )


def DownloadAssetObjectFiles(path: Union[str, Path, os.PathLike, LiteralString], hash_value: str):
    path = Path(path)
    Path(path / hash_value[0:2]).mkdir(parents=True, exist_ok=True)
    file_path = Path(path / hash_value[0:2] / hash_value)
    if not file_path.exists():
        url = f"https://resources.download.minecraft.net/{hash_value[0:2]}/{hash_value}"
        response = requests.get(url)
        Path(file_path).write_bytes(response.content)
    else:
        sha1 = hashlib.sha1(Path(file_path).read_bytes())
        if sha1.hexdigest() != hash_value:
            url = f"https://resources.download.minecraft.net/{hash_value[0:2]}/{hash_value}"
            response = requests.get(url)
            Path(path).write_bytes(response.content)


def DownloadLibraryFiles(version: Union[str, None] = None,
                         minecraft_path: Union[str, Path, os.PathLike, LiteralString] = "."):
    if not version:
        return
    minecraft_path = Path(minecraft_path)
    response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    version_manifest = response.json()
    version_id = version
    version_info = None
    for version in version_manifest['versions']:
        if version['id'] == version_id:
            version_info = version
            break
    libraries_file_data = requests.get(version_info["url"])
    libraries_file_data = libraries_file_data.json()
    libraries_file_data = libraries_file_data["libraries"]
    for i in range(0, len(libraries_file_data)):
        if libraries_file_data[i].get("rules", None) is not None:
            try:
                rule_of_os = libraries_file_data[i]["rules"][0]["os"]["name"]
            except KeyError:
                rule_of_os = libraries_file_data[i]["rules"][1]["os"]["name"]
            if GetOperationSystem.GetOperationSystemInMojangApi()[0].lower() != rule_of_os:
                continue
        data = libraries_file_data[i]["downloads"]
        try:
            data_of_file = data["artifact"]
        except KeyError:
            data_of_file = data["classifiers"][f"natives-{GetOperationSystem.GetOperationSystemInMojangApi()[0]}"]
        libraries_dir_path = Path(minecraft_path / "libraries")
        path = Path(libraries_dir_path / Path(data_of_file["path"]))
        url = data_of_file["url"]
        if not Path(path).exists():
            _DownloadLibraryFile(url, path)


def download_game(minecraft_path: Union[str, Path, os.PathLike, LiteralString] = ".", version: Union[str, None] = None):
    minecraft_path = Path(minecraft_path)
    Path(minecraft_path / "versions" / version).mkdir(parents=True, exist_ok=True)
    if not Path(minecraft_path / "versions" / version / f"{version}.json").exists():
        DownloadVersionJson(version, minecraft_path)
    if not Path(minecraft_path / "versions" / version / f"{version}.jar").exists():
        client_url = GetMinecraftClientDownloadUrl(version=version)
        downloader = Downloader(client_url, f"{version}.jar", Path(minecraft_path / "versions" / version))
        downloader.download()
    DownloadLibraryFiles(minecraft_path=minecraft_path, version=version)
    DownloadAssetIndexFile(minecraft_path=minecraft_path,
                           json_path=Path(minecraft_path / "versions" / version / f"{version}.json"))
    asset_id = json.loads(Path(minecraft_path / "versions" / version / f"{version}.json").read_text(encoding="utf-8"))[
        "assetIndex"]["id"]
    for i in json.loads(Path(minecraft_path / "assets" / "indexes" / f"{asset_id}.json").read_text(encoding="utf-8"))[
        "objects"].values():
        DownloadAssetObjectFiles(Path(minecraft_path / "assets" / "objects"), i["hash"])
