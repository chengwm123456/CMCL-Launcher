# -*- coding: utf-8 -*-
import json
import os
import hashlib
import zipfile
from typing import *

import psutil
from pathlib import Path, PurePath
import subprocess
import shlex
from enum import Enum

from . import Downloader
from . import DownloadVersion
from . import GetVersion
from . import GetOperationSystem
from CMCLCore.CMCLGameLaunching.CommandGenerating import GenerateMinecraftLaunchCommand
from .CMCLDefines import Minecraft


class JavaMode(Enum):
    CLIENT = "client"
    SERVER = "server"


class QuickPlayMode(Enum):
    SINGLE_PLAYER = "SinglePlayer"
    MULTI_PLAYER = "MultiPlayer"
    REALMS = "Realms"


def GetJavaPath(version: Union[str, int]) -> Optional[Union[str, Path]]:
    where_out = subprocess.run(
        ["which" if GetOperationSystem.GetOperationSystemName()[0].lower() != "windows" else "where", "java"],
        capture_output=True,
        check=False).stdout
    java_path = where_out.decode(errors="ignore").splitlines()
    if len(java_path) >= 2 and not java_path[-1]:
        del java_path[-1]
    if Path(java_path[0]).exists():
        for i in java_path:
            if Path(i).is_file():
                try:
                    version_data = \
                        subprocess.check_output([i, "--version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                            0].split(
                            " ")[1].split(".")[0].lstrip('"')
                except subprocess.CalledProcessError:
                    version_data = \
                        subprocess.check_output([i, "-version"], stderr=subprocess.STDOUT,
                                                creationflags=subprocess.CREATE_NO_WINDOW).decode().splitlines()[
                            0].split(
                            " ")[2].split(".")[1].lstrip('"')
                if str(version) == version_data:
                    return i
    java_home = os.getenv('JAVA_HOME')
    if java_home:
        java_path = Path(Path(java_home) / 'bin' / 'java.exe')
        if Path(java_path).is_file():
            version_data = \
                subprocess.check_output([java_path, "--version"], stderr=subprocess.STDOUT,
                                        creationflags=subprocess.CREATE_NO_WINDOW).decode().split("\r\n")[
                    0].split(" ")[1].split(".")[0].lstrip('"')
            if str(version) == version_data:
                return java_path
    return None


def FixMinecraftFiles(minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString], version_fix: str):
    if not Path(minecraft_path).exists():
        os.makedirs(minecraft_path)
    os.chdir(minecraft_path)
    if not Path(minecraft_path / "versions" / version_fix / f"{version_fix}.json").exists():
        DownloadVersion.DownloadVersionJson(version=version_fix, minecraft_path=minecraft_path)
    file = Path(minecraft_path / "versions" / version_fix / f"{version_fix}.json")
    jsons = json.loads(file.read_text(encoding="utf-8"))
    file = Path(minecraft_path / "assets" / "indexes" / f"{jsons['assets']}.json")
    data = json.loads(file.read_text(encoding="utf-8"))
    data = bytes(str(data).replace("'", '"'), "utf-8")
    sha1 = hashlib.sha1(data)
    if sha1.hexdigest() != jsons['assetIndex']['sha1']:
        DownloadVersion.DownloadAssetIndexFile(json_path=os.path.join(minecraft_path, "versions",
                                                                      version_fix,
                                                                      f"{version_fix}.json"),
                                               minecraft_path=minecraft_path)
    assets = json.loads(file.read_text(encoding="utf-8"))
    for i in assets["objects"]:
        filedata = assets["objects"][i]
        filehash = filedata["hash"]
        path = os.path.join(minecraft_path, "assets", "objects", filehash[0:2], filehash)
        file = Path(str(path))
        if file.exists():
            sha1 = hashlib.sha1(file.read_bytes())
            if sha1.hexdigest() != filehash:
                DownloadVersion.DownloadAssetObjectFiles(os.path.join(minecraft_path, "assets", "objects"),
                                                         filehash)
        else:
            DownloadVersion.DownloadAssetObjectFiles(os.path.join(minecraft_path, "assets", "objects"), filehash)
    libraries_file_data = jsons["libraries"]
    for i in range(0, len(libraries_file_data)):
        is_changed = False
        data = libraries_file_data[i]["downloads"]
        try:
            data_of_file = data["artifact"]
        except KeyError:
            data_of_file = data["classifiers"][f"natives-{GetOperationSystem.GetOperationSystemInMojangApi()[0]}"]
        libraries_dir_path = os.path.join(minecraft_path, "libraries")
        path = os.path.join(libraries_dir_path, data_of_file["path"].replace("/", os.sep))
        if Path(path).exists():
            if not Path(os.path.dirname(path)).exists():
                os.makedirs(os.path.dirname(path))
            file = Path(str(path))
            sha1 = hashlib.sha1(file.read_bytes())
            if sha1.hexdigest() != data_of_file['sha1']:
                is_changed = True
        if not Path(path).exists() or is_changed:
            if libraries_file_data[i].get("rules", None) is not None:
                try:
                    rule_of_os = libraries_file_data[i]["rules"][0]["os"]["name"]
                except KeyError:
                    rule_of_os = libraries_file_data[i]["rules"][1]["os"]["name"]
                if GetOperationSystem.GetOperationSystemInMojangApi()[0].lower() != rule_of_os:
                    continue
            downloader = Downloader.Downloader(data_of_file["url"], path)
            downloader.download()
    game_jar_path = os.path.join(minecraft_path, "versions", version_fix, f"{version_fix}.jar")
    file = Path(str(game_jar_path))
    sha1 = hashlib.sha1(file.read_bytes())
    if sha1.hexdigest() != jsons["downloads"]["client"]["sha1"]:
        url = GetVersion.GetMinecraftClientDownloadUrl(version=version_fix)
        downloader = Downloader.Downloader(url, os.path.join(minecraft_path, "versions", version_fix,
                                                             f"{version_fix}.jar"))
        downloader.download()


def UnpackMinecraftNativeFiles(
        minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString],
        version_launch: str
):
    jsons = json.loads(
        Path(minecraft_path / "versions" / version_launch / f"{version_launch}.json").read_text(encoding="utf-8"))
    libraries_file_data = jsons["libraries"]
    for lib in libraries_file_data:
        unpack = bool(lib.get("downloads", {}).get("classifiers")) and \
                 GetOperationSystem.GetOperationSystemInMojangApi()[0] in \
                 lib[
                     "natives"]
        data = lib.get("downloads", {})
        libraries_dir_path = Path(minecraft_path / "libraries")
        path_artifact = None
        if data.get("artifact"):
            path_artifact = Path(libraries_dir_path / data["artifact"]["path"])
        if data.get("classifiers") and GetOperationSystem.GetOperationSystemInMojangApi()[0] in lib[
            "natives"] and f"natives-{GetOperationSystem.GetOperationSystemInMojangApi()[0]}" in data.get(
            "classifiers").keys() and unpack:
            path_classifiers = Path(libraries_dir_path / data["classifiers"].get(
                f"natives-{GetOperationSystem.GetOperationSystemInMojangApi()[0]}")["path"])
            if not path_classifiers:
                path_classifiers = path_artifact
            try:
                print(path_classifiers, Path(path_classifiers).exists())
                exclude = data.get("extract", {}).get("exclude", [])
                natives_jar = zipfile.ZipFile(path_classifiers, "r")
                if exclude:
                    for i in natives_jar.filelist:
                        filename = PurePath(i.filename)
                        for j in exclude:
                            if PurePath(j).parts in filename.parts:
                                break
                        else:
                            natives_jar.extract(i, PurePath(
                                minecraft_path / "versions" / version_launch / f"{version_launch}-natives") / filename)
                else:
                    natives_jar.extractall(
                        PurePath(minecraft_path / "versions" / version_launch / f"{version_launch}-natives"))
            except FileNotFoundError:
                pass


def LaunchMinecraft(
        minecraft_path=None,
        version_launch=None,
        java_path=None,
        launch_mode="client",
        launcher_version="",
        launcher_name="CMCL",
        initial_memory=None,
        max_memory=None,
        jvm_arg_options=None,
        extra_game_command="",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        player_data=None,
        **kw
):
    if not version_launch:
        return "Unsuccessfully", "cannout launch without specified a version to launch"
    minecraft_path = Path(minecraft_path or '.').absolute()
    minecraft_path.mkdir(parents=True, exist_ok=True)
    quickplay_mode = kw.get("quickplay_mode", "")
    if quickplay_mode is not None:
        match quickplay_mode:
            case QuickPlayMode.SINGLE_PLAYER:
                passkey = "--quickPlaySingleplayer"
                world_name = kw.get("world_name")
                quickplay_command = passkey + " " + world_name
            case QuickPlayMode.MULTI_PLAYER:
                passkey = "--quickPlayMultiplayer"
                host_port_link_name = kw.get("host_port_link")
                quickplay_command = passkey + " " + host_port_link_name
            case QuickPlayMode.REALMS:
                passkey = "--quickPlayRealms"
                server_id = kw.get("server_id")
                quickplay_command = passkey + " " + server_id
            case _:
                quickplay_command = ""
    else:
        quickplay_command = ""
    if not Path(minecraft_path / "versions" / version_launch / f"{version_launch}.json").exists():
        return "Unsuccessfully", "cannot launch without version json file"
    jsons = json.loads(
        Path(minecraft_path / "versions" / version_launch / f"{version_launch}.json").read_text(encoding="utf-8"))
    Path(minecraft_path / "libraries").mkdir(parents=True, exist_ok=True)
    if not Path(minecraft_path / "assets" / "indexes" / f"{jsons['assets']}.json").exists():
        return "Unsuccessfully", "cannot launch without asset file"
    if not java_path:
        for i in range(int(jsons["javaVersion"]["majorVersion"]), 999):
            java_path = GetJavaPath(str(i))
            if java_path is not None:
                break
        else:
            return "Unsuccessfully", "cannot launch without a Java"
    if not player_data:
        return "Unsuccessfully", "wrong player data"
    # with open(os.path.join(minecraft_path, "options.txt"), "r", encoding="utf-8") as file:
    #     info = file.readlines()
    #     for e, i in enumerate(info):
    #         print(i)
    #         if "lang:" in i:
    #             j = i.split(":")
    #             print(j)
    #             if j[1] != "zh_cn":
    #                 j[1] = "zh_cn"
    #             i = f"{i[0]}:{i[1]}"
    #             info[e] = i
    # info = os.linesep.join(info)
    # with open(os.path.join(minecraft_path, "options.txt"), "w", encoding="utf-8") as file:
    #     file.write(info)
    jvm_args = [
        f'-{launch_mode}',
        '-XX:+UseG1GC',
        '-XX:+UseAdaptiveSizePolicy',
        '-XX:MaxInlineSize=420',
        '-XX:+TieredCompilation',
        '-XX:+ParallelRefProcEnabled',
        '-XX:MaxGCPauseMillis=152',
        '-XX:+UnlockExperimentalVMOptions',
        '-XX:+UnlockDiagnosticVMOptions',
        '-XX:+Inline',
        '-XX:+DisableExplicitGC',
        '-XX:+AlwaysPreTouch',
        '-XX:G1NewSizePercent=30',
        '-XX:G1MaxNewSizePercent=40',
        '-XX:G1HeapRegionSize=8M',
        '-XX:G1ReservePercent=20',
        '-XX:G1HeapWastePercent=5',
        '-XX:G1MixedGCCountTarget=4',
        '-XX:InitiatingHeapOccupancyPercent=15',
        '-XX:G1MixedGCLiveThresholdPercent=90',
        '-XX:G1RSetUpdatingPauseTimePercent=5',
        '-XX:SurvivorRatio=31',
        '-XX:+PerfDisableSharedMem',
        f'-XX:ParallelGCThreads={psutil.cpu_count()}',
        f'-XX:ConcGCThreads={psutil.cpu_count()}',
        '-XX:MaxTenuringThreshold=1',
        '-Dfml.ignoreInvalidMinecraftCertificates=True',
        '-Dfml.ignorePatchDiscrepancies=True',
        '-Dlog4j2.formatMsgNoLookups=true',
        '-Dfile.encoding=UTF-8',
        '-Dstdout.encoding=UTF-8',
        '-Dstderr.encoding=UTF-8',

        '-Dorg.lwjgl.util.DebugLoader=true',
        '-Dorg.lwjgl.util.Debug=true',
    ]
    minecraft = Minecraft.Minecraft(version=version_launch, game_work_dir=minecraft_path,
                                    game_jar=minecraft_path / "versions" / version_launch / f"{version_launch}.jar",
                                    game_json=minecraft_path / "versions" / version_launch / f"{version_launch}.json",
                                    game_natives_dir=minecraft_path / "versions" / version_launch / f"{version_launch}-natives",
                                    game_libs=minecraft_path / "libraries", game_asset_dir=minecraft_path / "assets", )
    initial_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
    max_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
    command = GenerateMinecraftLaunchCommand(java_path, minecraft, player_data,
                                             jvm_args, extra_game_command, quickplay_command, initial_memory,
                                             max_memory, launcher_name, launcher_version)
    print(command)
    UnpackMinecraftNativeFiles(minecraft_path, version_launch)
    # if not stdout:
    #     stdout = subprocess.STDOUT
    # if not stderr:
    #     stderr = subprocess.STDOUT
    game = subprocess.Popen(
        shlex.split(command),
        stdout=stdout,
        stderr=stderr,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        cwd=str(minecraft_path)
    )
    # print(detect(output), output.decode(detect(output)['encoding']))
    return "Successfully", game
