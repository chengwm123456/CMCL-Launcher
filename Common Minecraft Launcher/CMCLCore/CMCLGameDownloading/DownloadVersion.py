# -*- coding: utf-8 -*-
from typing import *

import hashlib
import json
from pathlib import PurePath
from concurrent.futures import ThreadPoolExecutor, as_completed

from .. import GetOperationSystem
from ..CMCLDefines.Downloader import Downloader
from ..GetVersion import *
from ..CMCLMirrorMappings import GetMirrorSourceUrl


def DownloadVersionJson(
        version: Optional[Union[str]] = None,
        minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
        version_path: Optional[Union[str]] = None
):
    if not version:
        return
    if not version_path:
        version_path = version
    minecraft_path = Path(minecraft_path)
    version_manifest = GetVersionsByMojangAPI(returns="RETURN_JSON")
    version_id = version
    version_info = None
    for v in version_manifest['versions']:
        if v['id'] == version_id:
            version_info = v
            break
    json_url = requests.get(GetMirrorSourceUrl(version_info["url"]))
    json_info = json_url.json()
    path = Path(minecraft_path / "versions" / version_path,
                f"{version_path}.json")
    Path(path).write_text(
        json.dumps(
            json_info,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def DownloadLibraryFile(url: str, path: Union[str, Path, PurePath, os.PathLike, LiteralString] = "."):
    path, file_name = Path(*(Path(path).parts[:-1])), Path(Path(path).parts[-1])
    Path(path).mkdir(parents=True, exist_ok=True)
    file_path = Path(path / file_name)
    if not Path(file_path).exists():
        file_path.write_bytes(requests.get(url).content)


def DownloadAssetIndexFile(minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
                           json_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = "."):
    minecraft_path = Path(minecraft_path)
    assets_file_data = json.loads(Path(json_path).read_text(encoding="utf-8"))["assetIndex"]
    if not Path(minecraft_path / "assets" / "indexes").exists():
        os.makedirs(Path(minecraft_path / "assets" / "indexes"))
    file_path = Path(minecraft_path / "assets" / "indexes" / f"{assets_file_data['id']}.json")
    if not Path(file_path).exists():
        response = requests.get(GetMirrorSourceUrl(assets_file_data["url"]))
        assets_info = response.json()
        Path(file_path).write_text(
            json.dumps(
                assets_info,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
    # else:
    #     sha1 = hashlib.sha1(Path(file_path).read_bytes())
    #     if sha1.hexdigest() != assets_file_data["sha1"]:
    #         response = requests.get(GetMirrorSourceUrl(assets_file_data["url"]))
    #         assets_info = response.json()
    #         Path(file_path).write_text(
    #             json.dumps(
    #                 assets_info,
    #                 indent=2,
    #                 ensure_ascii=False
    #             ),
    #             encoding="utf-8"
    #         )


def DownloadAssetObjectFile(path: Union[str, Path, PurePath, os.PathLike, LiteralString], hash_value: str):
    path = Path(path)
    Path(path / hash_value[0:2]).mkdir(parents=True, exist_ok=True)
    file_path = Path(path / hash_value[0:2] / hash_value)
    if not file_path.exists():
        url = GetMirrorSourceUrl(f"https://resources.download.minecraft.net/{hash_value[0:2]}/{hash_value}")
        response = requests.get(url)
        Path(file_path).write_bytes(response.content)
    # else:
    #     sha1 = hashlib.sha1(Path(file_path).read_bytes())
    #     if sha1.hexdigest() != hash_value:
    #         url = f"https://resources.download.minecraft.net/{hash_value[0:2]}/{hash_value}"
    #         response = requests.get(url)
    #         Path(path).write_bytes(response.content)


def DownloadAssetsObjectFiles(minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString],
                              asset_id: Union[str, int],
                              **options):
    futures = []
    with ThreadPoolExecutor(max_workers=options.get("max_workers", 8)) as executor:
        for i in json.loads(Path(minecraft_path / "assets" / "indexes" / f"{str(asset_id)}.json").read_text(
                encoding="utf-8"))["objects"].values():
            futures.append(executor.submit(
                DownloadAssetObjectFile,
                Path(minecraft_path / "assets" / "objects"),
                i["hash"]
            ))
    
    futures = [future.result() for future in as_completed(futures)]


def DownloadLibraryFiles(version: Union[str, None] = None,
                         minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
                         **options):
    if not version:
        return
    minecraft_path = Path(minecraft_path)
    version_manifest = GetVersionsByMojangAPI(returns="RETURN_JSON")
    version_id = version
    version_info = None
    for version in version_manifest['versions']:
        if version['id'] == version_id:
            version_info = version
            break
    libraries_file_data = requests.get(GetMirrorSourceUrl(version_info["url"]))
    libraries_file_data = libraries_file_data.json()
    libraries_file_data = libraries_file_data["libraries"]
    
    futures = []
    with ThreadPoolExecutor(max_workers=options.get("max_workers", 8)) as executor:
        for i in range(0, len(libraries_file_data)):
            if libraries_file_data[i].get("rules", None) is not None:
                try:
                    rule_of_os = libraries_file_data[i]["rules"][0]["os"]["name"]
                except KeyError:
                    rule_of_os = libraries_file_data[i]["rules"][1]["os"]["name"]
                if GetOperationSystem.GetOperationSystemInMojangAPI()[0].lower() != rule_of_os:
                    continue
            data = libraries_file_data[i]["downloads"]
            try:
                data_of_file = data["artifact"]
            except KeyError:
                data_of_file = data["classifiers"][f"natives-{GetOperationSystem.GetOperationSystemInMojangAPI()[0]}"]
            libraries_dir_path = Path(minecraft_path / "libraries")
            path = Path(libraries_dir_path / Path(data_of_file["path"]))
            url = GetMirrorSourceUrl(data_of_file["url"])
            if not Path(path).exists():
                futures.append(executor.submit(
                    DownloadLibraryFile,
                    url,
                    path
                ))
    
    futures = [future.result() for future in as_completed(futures)]


def DownloadMinecraft(
        minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
        version: Optional[Union[str]] = None,
        version_path: Optional[Union[str]] = None,
        **options
):
    if not version:
        return
    if not version_path:
        version_path = version
    minecraft_path = Path(minecraft_path)
    Path(minecraft_path / "versions" / version_path).mkdir(parents=True, exist_ok=True)
    if not Path(minecraft_path / "versions" / version_path / f"{version_path}.json").exists():
        DownloadVersionJson(version, minecraft_path)
    if not Path(minecraft_path / "versions" / version_path / f"{version_path}.jar").exists():
        client_url = GetMinecraftClientDownloadUrl(version=version)
        downloader = Downloader(client_url, f"{version_path}.jar", Path(minecraft_path / "versions" / version_path),
                                maximum_threads=options.get("max_workers", 8),
                                chunk_size=options.get("chunk_size", 1024 * 1024 * 8))
        downloader.downloadFile()
    DownloadLibraryFiles(minecraft_path=minecraft_path, version=version, max_workers=options.get("max_workers", 8))
    DownloadAssetIndexFile(minecraft_path=minecraft_path,
                           json_path=Path(minecraft_path / "versions" / version_path / f"{version_path}.json"))
    asset_id = json.loads(
        Path(minecraft_path / "versions" / version_path / f"{version_path}.json").read_text(encoding="utf-8"))[
        "assetIndex"]["id"]
    DownloadAssetsObjectFiles(minecraft_path=minecraft_path, asset_id=asset_id,
                              max_workers=options.get("max_workers", 8))
