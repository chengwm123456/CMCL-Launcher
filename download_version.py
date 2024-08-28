# -*- coding: utf-8 -*-
import hashlib
import json

import get_os
from download_file import Downloader
from getversion import *


def download_version_json(version=None, minecraft_path="."):
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


def _download_library_file(url, path):
    path, file_name = os.path.splitext(path)
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, file_name)
    if not os.path.exists(file_path):
        downloader = Downloader(url, file_path)
        downloader.download()


def download_asset_index_file(minecraft_path=".", json_path="."):
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


def download_assets_objects_file(path, hash_value):
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


def download_library_files(version=None, minecraft_path="."):
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
            if get_os.getOperationSystemInMojangApi()[0].lower() != rule_of_os:
                continue
        data = libraries_file_data[i]["downloads"]
        try:
            data_of_file = data["artifact"]
        except KeyError:
            data_of_file = data["classifiers"][f"natives-{get_os.getOperationSystemInMojangApi()[0]}"]
        libraries_dir_path = Path(minecraft_path / "libraries")
        path = Path(libraries_dir_path / Path(data_of_file["path"]))
        url = data_of_file["url"]
        if not Path(path).exists():
            _download_library_file(url, path)


def download_game(minecraft_path=".", version=None):
    minecraft_path = Path(minecraft_path)
    Path(minecraft_path / "versions" / version).mkdir(parents=True, exist_ok=True)
    if not Path(minecraft_path / "versions" / version / f"{version}.json").exists():
        download_version_json(version, minecraft_path)
    if not Path(minecraft_path / "versions" / version / f"{version}.jar").exists():
        client_url = get_download_url(version=version)
        downloader = Downloader(client_url, f"{version}.jar", Path(minecraft_path / "versions" / version))
        downloader.download()
    download_library_files(minecraft_path=minecraft_path, version=version)
    download_asset_index_file(minecraft_path=minecraft_path,
                              json_path=Path(minecraft_path / "versions" / version / f"{version}.json"))
    asset_id = json.loads(Path(minecraft_path / "versions" / version / f"{version}.json").read_text(encoding="utf-8"))[
        "assetIndex"]["id"]
    for i in json.loads(Path(minecraft_path / "assets" / "indexes" / f"{asset_id}.json").read_text(encoding="utf-8"))[
        "objects"].values():
        download_assets_objects_file(Path(minecraft_path / "assets" / "objects"), i["hash"])
