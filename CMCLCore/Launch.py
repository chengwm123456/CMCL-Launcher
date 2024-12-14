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
from .CMCLDefines import Player
from .Player import AuthlibInjectorPlayer


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


def GenerateMinecraftLaunchCommand(
        minecraft_path: Union[str, Path, PurePath, os.PathLike, LiteralString],
        java_path: Union[str, Path, PurePath, os.PathLike, LiteralString],
        version_launch: str,
        player_data: Player,
        jvm_arguments: Optional[Union[str, list]],
        extra_game_command: str,
        quickplay_command: str,
        initial_memory: int,
        max_memory: int,
        launcher_name: str,
        launcher_version: str,
) -> str:
    # TODO: test the Minecraft launch command generation correction rate and launch Minecraft success rate on Linux
    minecraft_path = Path(minecraft_path).absolute()
    mc_json = json.loads(
        Path(minecraft_path / "versions" / version_launch / f"{version_launch}.json").read_text(encoding="utf-8"))
    mc_libraries_file_datas = mc_json.get("libraries", [])
    mc_libraries_files = []
    mc_libraries_files_names = {}
    for mc_lib in mc_libraries_file_datas:
        if mc_lib.get("downloads"):
            if mc_lib.get("rules"):
                action = "disallow"
                for rule in mc_lib.get("rules", []):
                    rule_of_os = rule.get("os", {}).get("name", GetOperationSystem.GetOperationSystemInMojangApi()[0])
                    if rule_of_os != GetOperationSystem.GetOperationSystemInMojangApi()[0]:
                        continue
                    action = rule.get("action", action)
                allow = bool(mc_lib.get("downloads", {}).get("artifact", {})) and action == "allow"
            else:
                allow = bool(mc_lib.get("downloads", {}).get("artifact", {}))
            downloads = mc_lib.get("downloads", {})
            # mc_libraries_path = Path(minecraft_path / "libraries")
            if downloads.get("artifact") and allow:
                # mc_lib_path_artifact = Path(mc_libraries_path / downloads.get("artifact", {}).get("path", ""))
                mc_libraries_path = Path(minecraft_path / "libraries")
                mc_lib_name = mc_lib.get("name", "::")
                names = mc_lib_name.split(":")
                mc_lib_base_path = Path(Path(names[0].replace(".", "/")) / names[1])
                mc_lib_secondary_path = Path(Path(names[2]) / f"{names[1]}-{names[2]}.jar")
                mc_lib_path = Path(mc_lib_base_path / mc_lib_secondary_path)
                mc_lib_path_artifact = Path(mc_libraries_path / mc_lib_path)
                if tuple(names[:-1]) in mc_libraries_files_names:
                    mc_libraries_files[mc_libraries_files_names[tuple(names[:-1])]] = str(mc_lib_path_artifact)
                else:
                    mc_libraries_files.append(str(mc_lib_path_artifact))
                mc_libraries_files_names[tuple(names[:-1])] = len(mc_libraries_files) - 1
        else:
            mc_libraries_path = Path(minecraft_path / "libraries")
            mc_lib_name = mc_lib.get("name", "::")
            names = mc_lib_name.split(":")
            mc_lib_base_path = Path(Path(names[0].replace(".", "/")) / names[1])
            mc_lib_secondary_path = Path(Path(names[2]) / f"{names[1]}-{names[2]}.jar")
            mc_lib_path = Path(mc_lib_base_path / mc_lib_secondary_path)
            mc_lib_path_artifact = Path(mc_libraries_path / mc_lib_path)
            if tuple(names[:-1]) in mc_libraries_files_names:
                mc_libraries_files[mc_libraries_files_names[tuple(names[:-1])]] = str(mc_lib_path_artifact)
            else:
                mc_libraries_files.append(str(mc_lib_path_artifact))
            mc_libraries_files_names[tuple(names[:-1])] = len(mc_libraries_files) - 1
    mc_libraries_files = (":" if not GetOperationSystem.GetOperationSystemName()[0] == "Windows" else ";").join(
        mc_libraries_files)
    if initial_memory is None or max_memory is None:
        initial_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
        max_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
    memory_args = f"-Xmn{str(initial_memory)} -Xmx{str(max_memory)}"
    game_jar_path = Path(minecraft_path / "versions" / version_launch / f"{version_launch}.jar")
    assets = mc_json.get("assets")
    main_class = mc_json.get("mainClass")
    version_type = mc_json.get("type")
    if not jvm_arguments:
        jvm_arguments = []
    if isinstance(jvm_arguments, str):
        jvm_arguments = shlex.split(jvm_arguments)
    mc_jvm_command = jvm_arguments
    if mc_json.get("arguments"):
        quick_started = False
        mc_arguments = mc_json["arguments"]
        mc_game_arguments = mc_arguments["game"]
        mc_game_command = []
        for arg in mc_game_arguments:
            if isinstance(arg, dict):
                if arg.get("value") == "--demo" and player_data.player_hasMC:
                    continue
                rules = arg.get("rules", [{}])[0]
                value = arg.get("value", "")
                features = rules.get("features", {})
                if features.values():
                    if isinstance(value, list):
                        for str_arg in value:
                            if value[0] in ["--quickPlaySingleplayer", "--quickPlayMultiplayer", "--quickPlayRealms"] \
                                    and not quick_started and quickplay_command is not None:
                                quick_started = True
                                mc_game_command.append(quickplay_command)
                                continue
                            else:
                                if value[0] in ["--quickPlaySingleplayer",
                                                "--quickPlayMultiplayer",
                                                "--quickPlayRealms"]:
                                    continue
                                str_arg = str_arg.replace("${resolution_width}", "854")
                                str_arg = str_arg.replace("${resolution_height}", "480")
                                mc_game_command.append(str_arg)
                    else:
                        str_arg = value
                        str_arg = str_arg.replace("${resolution_width}", "854")
                        str_arg = str_arg.replace("${resolution_height}", "480")
                        mc_game_command.append(str_arg)
            else:
                str_arg = arg
                str_arg = str_arg.replace("${auth_player_name}", f'"{player_data.player_name}"')
                str_arg = str_arg.replace("${version_name}", f'"{version_launch}"')
                str_arg = str_arg.replace("${game_directory}", f'"{minecraft_path}"')
                str_arg = str_arg.replace("${assets_root}", f'"{Path(minecraft_path / "assets")}"')
                str_arg = str_arg.replace("${assets_index_name}", f'"{assets}"')
                str_arg = str_arg.replace("${auth_uuid}", f'"{player_data.player_uuid}"')
                str_arg = str_arg.replace("${auth_access_token}", f'"{player_data.player_accessToken}"')
                str_arg = str_arg.replace("${clientid}", f"${{clientid}}")
                str_arg = str_arg.replace("${auth_xuid}", f"${{auth_xuid}}")
                str_arg = str_arg.replace("${user_type}", f'"{player_data.player_accountType[1]}"')
                str_arg = str_arg.replace("${version_type}", f'"{version_type}"')
                mc_game_command.append(str_arg)
        if extra_game_command:
            mc_game_command.append(extra_game_command.strip(" "))
        mc_game_command = " ".join(mc_game_command)
        mc_jvm_arguments = mc_arguments.get("jvm", [])
        for arg in mc_jvm_arguments:
            if isinstance(arg, dict):
                rules = arg["rules"][0]
                os_data = GetOperationSystem.GetOperationSystemInMojangApi()
                os_rules = rules["os"]
                if os_rules.get("name") and os_rules["name"] != os_data[0]:
                    continue
                if os_rules.get("arch") and os_data[1] != os_rules["arch"]:
                    continue
                value = arg["value"]
                if isinstance(value, list):
                    for one_val in value:
                        if " " in one_val and '"' not in one_val:
                            one_val = f'"{shlex.quote(one_val)[1:-1]}"'
                        mc_jvm_command.append(one_val)
                else:
                    mc_jvm_command.append(value)
            else:
                natives_dir = Path(minecraft_path / "versions" / version_launch / f"{version_launch}-natives")
                str_arg = arg
                if " " in str_arg:
                    str_arg = f'"{shlex.quote(str_arg)[1:-1]}"'
                str_arg = str_arg.replace("${natives_directory}", f'"{natives_dir}"')
                str_arg = str_arg.replace("${launcher_name}", f'"{launcher_name}"')
                str_arg = str_arg.replace("${launcher_version}", f'"{launcher_version}"')
                str_arg = str_arg.replace("${classpath}",
                                          f'"{mc_libraries_files}{":" if GetOperationSystem.GetOperationSystemName()[0] != "Windows" else ";"}{game_jar_path}"')
                mc_jvm_command.append(str_arg)
        mc_jvm_command.append(memory_args)
        mc_jvm_command.append(
            f"-Xmixed {main_class}")
        mc_jvm_command = " ".join(mc_jvm_command)
    elif mc_json.get("minecraftArguments"):
        mc_game_command = mc_json["minecraftArguments"]
        mc_game_command = mc_game_command.replace("${auth_session}", f'"{player_data.player_accessToken}"')
        mc_game_command = mc_game_command.replace("${auth_player_name}", f'"{player_data.player_name}"')
        mc_game_command = mc_game_command.replace("${version_name}", f'"{version_launch}"')
        mc_game_command = mc_game_command.replace("${game_directory}", f'"{minecraft_path}"')
        mc_game_command = mc_game_command.replace("${assets_root}",
                                                  f'"{Path(minecraft_path / "assets" / "virtual" / "legacy")}"')
        mc_game_command = mc_game_command.replace("${game_assets}",
                                                  f'"{Path(minecraft_path / "assets" / "virtual" / "legacy")}"')
        mc_game_command = mc_game_command.replace("${assets_index_name}", f'"{assets}"')
        mc_game_command = mc_game_command.replace("${auth_uuid}", f'"{player_data.player_uuid}"')
        mc_game_command = mc_game_command.replace("${auth_access_token}", f'"{player_data.player_accessToken}"')
        # c = c.replace("${clientid}", "${clientid}")
        # c = c.replace("${auth_xuid}", "${auth_xuid}")
        mc_game_command = mc_game_command.replace("${user_type}", f'"{player_data.player_accountType[1]}"')
        mc_game_command = mc_game_command.replace("${version_type}", f'"{version_type}"')
        if extra_game_command:
            mc_game_command = shlex.split(mc_game_command)
            mc_game_command.append(extra_game_command.strip(" "))
            mc_game_command = " ".join(mc_game_command)
        mc_jvm_command = f"{' '.join(mc_jvm_command)} -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump -Djava.library.path=\"{str(Path(minecraft_path / 'versions' / version_launch / f'{version_launch}-natives'))}\" -cp \"{mc_libraries_files}{':' if GetOperationSystem.GetOperationSystemName()[0] != 'Windows' else ';'}{game_jar_path}\" {memory_args} -Xmixed {main_class}"
    else:
        mc_jvm_command = mc_game_command = ""
    if isinstance(player_data, AuthlibInjectorPlayer):
        authlib_injector_jar_path = Path(r".\authlib-injector.jar")
        authentication_server_url = player_data.player_authServer  # "https://littleskin.cn/api/yggdrasil"
        signature_publickey = player_data.player_signaturePublickey.replace("\n", "")
        mc_authlib_injector_command = " ".join(
            [
                f'-javaagent:"{shlex.quote(str(authlib_injector_jar_path)[1:-1])}"="{shlex.quote(authentication_server_url)[1:-1]}"',
                '-Dauthlibinjector.side="client"',
                f'-Dauthlibinjector.yggdrasil.prefetched="{shlex.quote(signature_publickey)[1:-1]}"'
            ]
        )
    else:
        mc_authlib_injector_command = ""
    command = f'"{java_path.strip(chr(34))}" {mc_authlib_injector_command} {mc_jvm_command} {mc_game_command}'
    return command


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
        '-Dlog4j2.formatMsgNoLookups=true'
    ]
    command = GenerateMinecraftLaunchCommand(minecraft_path, java_path, version_launch, player_data,
                                             jvm_args, extra_game_command, quickplay_command, initial_memory,
                                             max_memory, launcher_name, launcher_version)
    print(command)
    UnpackMinecraftNativeFiles(minecraft_path, version_launch)
    game = subprocess.Popen(
        shlex.split(command),
        stdout=stdout,
        stderr=stderr,
        creationflags=subprocess.CREATE_NO_WINDOW,
        cwd=str(minecraft_path)
    )
    # print(detect(output), output.decode(detect(output)['encoding']))
    return "Successfully", game
