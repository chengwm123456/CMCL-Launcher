# -*- coding: utf-8 -*-
import json
import os
import hashlib
import re
import zipfile

import psutil
from pathlib import Path
import subprocess
import shlex
from enum import Enum

import download_file
import download_version
import getversion
import get_os


class JavaMode(Enum):
    CLIENT = "client"
    SERVER = "server"


class QuickPlayMode(Enum):
    SINGLE_PLAYER = "SinglePlayer"
    MULTI_PLAYER = "MultiPlayer"
    REALMS = "Realms"


report_description_lists = {
    "Manually triggered debug crash": "通过调试功能崩溃",
    "Reading NBT data": "读取NBT数据时崩溃"
}


def get_java_path(version):
    where_out = subprocess.run(["which" if get_os.getOperationSystemName()[0] != "Windows" else "where", "java"],
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
                if version == version_data:
                    return i
    java_home = os.getenv('JAVA_HOME')
    if java_home:
        java_path = Path(Path(java_home) / 'bin' / 'java.exe')
        if Path(java_path).is_file():
            version_data = \
                subprocess.check_output([java_path, "--version"], stderr=subprocess.STDOUT,
                                        creationflags=subprocess.CREATE_NO_WINDOW).decode().split("\r\n")[
                    0].split(" ")[1].split(".")[0].lstrip('"')
            if version == version_data:
                return java_path
    
    programme_files = os.getenv('ProgramFiles')
    if programme_files:
        java_path = Path(Path(programme_files) / 'Java')
        if os.path.isdir(java_path):
            for subdir in os.listdir(java_path):
                if subdir.startswith('jdk') and version in subdir:
                    java_path = Path(java_path / subdir / 'bin' / 'java.exe')
                    if Path(java_path).is_file():
                        version_data = \
                            subprocess.check_output([java_path, "--version"], stderr=subprocess.STDOUT,
                                                    creationflags=subprocess.CREATE_NO_WINDOW).decode().split(
                                "\r\n")[0].split(" ")[1].split(".")[0].lstrip('"')
                        if version == version_data:
                            return java_path
    
    return None


def fix_minecraft_files(minecraft_path, version_fix):
    if not Path(minecraft_path).exists():
        os.makedirs(minecraft_path)
    os.chdir(minecraft_path)
    if not Path(minecraft_path / "versions" / version_fix / f"{version_fix}.json").exists():
        download_version.download_version_json(version=version_fix, minecraft_path=minecraft_path)
    file = Path(minecraft_path / "versions" / version_fix / f"{version_fix}.json")
    jsons = json.loads(file.read_text(encoding="utf-8"))
    file = Path(minecraft_path / "assets" / "indexes" / f"{jsons['assets']}.json")
    data = json.loads(file.read_text(encoding="utf-8"))
    data = bytes(str(data).replace("'", '"'), "utf-8")
    sha1 = hashlib.sha1(data)
    if sha1.hexdigest() != jsons['assetIndex']['sha1']:
        download_version.download_asset_index_file(json_path=os.path.join(minecraft_path, "versions",
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
                download_version.download_assets_objects_file(os.path.join(minecraft_path, "assets", "objects"),
                                                              filehash)
        else:
            download_version.download_assets_objects_file(os.path.join(minecraft_path, "assets", "objects"), filehash)
    libraries_file_data = jsons["libraries"]
    for i in range(0, len(libraries_file_data)):
        is_changed = False
        data = libraries_file_data[i]["downloads"]
        try:
            data_of_file = data["artifact"]
        except KeyError:
            data_of_file = data["classifiers"][f"natives-{get_os.getOperationSystemInMojangApi()[0]}"]
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
                if get_os.getOperationSystemInMojangApi()[0].lower() != rule_of_os:
                    continue
            downloader = download_file.Downloader(data_of_file["url"], path)
            downloader.download()
    game_jar_path = os.path.join(minecraft_path, "versions", version_fix, f"{version_fix}.jar")
    file = Path(str(game_jar_path))
    sha1 = hashlib.sha1(file.read_bytes())
    if sha1.hexdigest() != jsons["downloads"]["client"]["sha1"]:
        url = getversion.get_download_url(version=version_fix)
        downloader = download_file.Downloader(url, os.path.join(minecraft_path, "versions", version_fix,
                                                                f"{version_fix}.jar"))
        downloader.download()


def unpack_natives_files(
        minecraft_path,
        version_launch
):
    jsons = json.loads(
        Path(minecraft_path / "versions" / version_launch / f"{version_launch}.json").read_text(encoding="utf-8"))
    libraries_file_data = jsons["libraries"]
    for lib in libraries_file_data:
        unpack = bool(lib.get("downloads", {}).get("classifiers")) and get_os.getOperationSystemInMojangApi()[0] in \
                 lib[
                     "natives"]
        data = lib.get("downloads", {})
        libraries_dir_path = Path(minecraft_path / "libraries")
        path_artifact = None
        if data.get("artifact"):
            path_artifact = Path(libraries_dir_path / data["artifact"]["path"])
        if data.get("classifiers") and get_os.getOperationSystemInMojangApi()[0] in lib[
            "natives"] and f"natives-{get_os.getOperationSystemInMojangApi()[0]}" in data.get(
            "classifiers").keys() and unpack:
            path_classifiers = Path(libraries_dir_path / data["classifiers"].get(
                f"natives-{get_os.getOperationSystemInMojangApi()[0]}")["path"])
            if not path_classifiers:
                path_classifiers = path_artifact
            try:
                print(path_classifiers, Path(path_classifiers).exists())
                zipfile.ZipFile(path_classifiers, "r").extractall(
                    Path(minecraft_path / "versions" / version_launch / f"{version_launch}-natives"))
            except FileNotFoundError:
                pass


def generate_launch_command(
        minecraft_path,
        java_path,
        version_launch,
        player_data,
        launch_mode,
        jvm_arg_options,
        extra_game_command,
        quickplay_command,
        initial_memory,
        max_memory,
        launcher_version
):
    jsons = json.loads(
        Path(minecraft_path / "versions" / version_launch / f"{version_launch}.json").read_text(encoding="utf-8"))
    libraries_file_data = jsons.get("libraries", [])
    libraries_files = []
    for lib in libraries_file_data:
        if lib.get("downloads"):
            if lib.get("rules"):
                action = "disallow"
                for rule in lib.get("rules", []):
                    rule_of_os = rule.get("os", {}).get("name", get_os.getOperationSystemInMojangApi()[0])
                    if rule_of_os != get_os.getOperationSystemInMojangApi()[0]:
                        continue
                    action = rule.get("action", action)
                allow = bool(lib.get("downloads", {}).get("artifact", {})) and action == "allow"
            else:
                allow = bool(lib.get("downloads", {}).get("artifact", {}))
            data = lib.get("downloads", {})
            libraries_dir_path = Path(minecraft_path / "libraries")
            if data.get("artifact") and allow:
                path_artifact = Path(libraries_dir_path / data.get("artifact", {}).get("path", ""))
                libraries_files.append(str(path_artifact))
        else:
            libraries_dir_path = Path(minecraft_path / "libraries")
            name = lib.get("name", "")
            names = name.split(":")
            path = Path(names[0].replace(".", "/")) / names[1]
            path_artifact = Path(libraries_dir_path / path)
            libraries_files.append(str(path_artifact))
    sep = ":" if not get_os.getOperationSystemName()[0] == "Windows" else ";"
    libraries_files = sep.join(libraries_files)
    if initial_memory is None or max_memory is None:
        initial_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
        max_memory = int(4294967296 * (psutil.virtual_memory().free / 4294967296))
    memory_args = f"-Xmn{str(initial_memory)} -Xmx{str(max_memory)}"
    player_name, player_uuid, player_access_token, player_type, player_has_mc = player_data
    game_jar_path = Path(minecraft_path / "versions" / version_launch / f"{version_launch}.jar")
    assets = jsons.get("assets")
    main_class = jsons.get("mainClass")
    version_type = jsons.get("type")
    launch_mode = JavaMode[launch_mode.upper()].value
    if jvm_arg_options is None:
        jvm_arg_options = {"option": "default"}
    match jvm_arg_options["option"]:
        case "default":
            jvmcommand = [f'-{launch_mode}',
                          '-XX:+UseG1GC',
                          '-XX:+UseAdaptiveSizePolicy',
                          '-XX:MaxInlineSize=420',
                          '-XX:+TieredCompilation',
                          '-XX:+ParallelRefProcEnabled',
                          '-XX:MaxGCPauseMillis=152',
                          '-XX:+UnlockExperimentalVMOptions',
                          '-XX:+UnlockDiagnosticVMOptions',
                          '-XX:+Inline',
                          # '-XX:+UseJVMCICompiler',
                          # '-XX:+EnableJVMCI',
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
                          '-Dlog4j2.formatMsgNoLookups=true']
        case "append":
            jvmcommand = [f'-{launch_mode}',
                          '-XX:+UseG1GC',
                          '-XX:+UseAdaptiveSizePolicy',
                          '-XX:MaxInlineSize=420',
                          '-XX:+TieredCompilation',
                          '-XX:+ParallelRefProcEnabled',
                          '-XX:MaxGCPauseMillis=152',
                          '-XX:+UnlockExperimentalVMOptions',
                          '-XX:+UnlockDiagnosticVMOptions',
                          '-XX:+Inline',
                          # '-XX:+UseJVMCICompiler',
                          # '-XX:+EnableJVMCI',
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
                          '-Dlog4j2.formatMsgNoLookups=true'].extend(jvm_arg_options["args"].split(" "))
        case "override":
            jvmcommand = jvm_arg_options["args"].split(" ")
        case _:
            jvmcommand = [f'-{launch_mode}',
                          '-XX:+UseG1GC',
                          '-XX:+UseAdaptiveSizePolicy',
                          '-XX:MaxInlineSize=420',
                          '-XX:+TieredCompilation',
                          '-XX:+ParallelRefProcEnabled',
                          '-XX:MaxGCPauseMillis=152',
                          '-XX:+UnlockExperimentalVMOptions',
                          '-XX:+UnlockDiagnosticVMOptions',
                          '-XX:+Inline',
                          # '-XX:+UseJVMCICompiler',
                          # '-XX:+EnableJVMCI',
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
                          '-Dlog4j2.formatMsgNoLookups=true']
    if jsons.get("arguments"):
        quick_started = False
        arguments = jsons["arguments"]
        gamearguments = arguments["game"]
        gamecommand = []
        for a in gamearguments:
            if isinstance(a, dict):
                if a["value"] == "--demo" and player_has_mc:
                    continue
                rules = a["rules"][0]
                value = a["value"]
                features = rules["features"]
                if features.values():
                    if isinstance(value, list):
                        for c in value:
                            if value[0] in ["--quickPlaySingleplayer", "--quickPlayMultiplayer", "--quickPlayRealms"] \
                                    and not quick_started and quickplay_command is not None:
                                quick_started = True
                                gamecommand.append(quickplay_command)
                                continue
                            else:
                                if value[0] in ["--quickPlaySingleplayer",
                                                "--quickPlayMultiplayer",
                                                "--quickPlayRealms"]:
                                    continue
                                c = c.replace("${resolution_width}", "854")
                                c = c.replace("${resolution_height}", "480")
                                gamecommand.append(c)
                    else:
                        c = value
                        c = c.replace("${resolution_width}", "854")
                        c = c.replace("${resolution_height}", "480")
                        gamecommand.append(c)
            else:
                c = a
                c = c.replace("${auth_player_name}", f'"{player_name}"')
                c = c.replace("${version_name}", f'"{version_launch}"')
                c = c.replace("${game_directory}", f'"{minecraft_path}"')
                c = c.replace("${assets_root}", f'"{Path(minecraft_path / "assets")}"')
                c = c.replace("${assets_index_name}", f'"{assets}"')
                c = c.replace("${auth_uuid}", f'"{player_uuid}"')
                c = c.replace("${auth_access_token}", f'"{player_access_token}"')
                c = c.replace("${clientid}", f"${{clientid}}")
                c = c.replace("${auth_xuid}", f"${{auth_xuid}}")
                c = c.replace("${player_accountType}", f'"{player_type}"')
                c = c.replace("${version_type}", f'"{version_type}"')
                gamecommand.append(c)
        if extra_game_command:
            gamecommand.append(extra_game_command.strip(" "))
        gamecommand = " ".join(gamecommand)
        jvmarguments = arguments["jvm"]
        for a in jvmarguments:
            if isinstance(a, dict):
                rules = a["rules"][0]
                os_data = get_os.getOperationSystemInMojangApi()
                os_rules = rules["os"]
                if os_rules.get("name") and os_rules["name"] != os_data[0]:
                    continue
                if os_rules.get("arch") and os_data[1] != os_rules["arch"]:
                    continue
                value = a["value"]
                if isinstance(value, list):
                    for i in value:
                        value_need = i.split("=")
                        value_need_str = value_need[1]
                        if " " in value_need_str and not (
                                value_need_str.startswith('"') and value_need_str.endswith('"')):
                            value_need_str = f'"{value_need_str}"'
                        i = f"{value_need[0]}={value_need_str}"
                        jvmcommand.append(i)
                else:
                    jvmcommand.append(value)
            else:
                natives_dir = Path(minecraft_path / "versions" / version_launch / f"{version_launch}-natives")
                c = a
                c = c.replace("${natives_directory}", f'"{natives_dir}"')
                c = c.replace("${launcher_name}", u'"CMCL"')
                c = c.replace("${launcher_version}", f'"{launcher_version}"')
                sep = ":" if get_os.getOperationSystemName()[0] != "Windows" else ";"
                c = c.replace("${classpath}", f'"{libraries_files}{sep}{game_jar_path}"')
                jvmcommand.append(c)
        jvmcommand.append(memory_args)
        jvmcommand.append(
            f"-Xmixed {main_class}")
        jvmcommand = " ".join(jvmcommand)
    elif jsons.get("minecraftArguments", None):
        gamecommand = jsons["minecraftArguments"]
        gamecommand = gamecommand.replace("${auth_session}", f'"{player_access_token}"')
        gamecommand = gamecommand.replace("${auth_player_name}", f'"{player_name}"')
        gamecommand = gamecommand.replace("${version_name}", f'"{version_launch}"')
        gamecommand = gamecommand.replace("${game_directory}", f'"{minecraft_path}"')
        gamecommand = gamecommand.replace("${assets_root}",
                                          f'"{Path(minecraft_path / "assets" / "virtual" / "legacy")}"')
        gamecommand = gamecommand.replace("${game_assets}",
                                          f'"{Path(minecraft_path / "assets" / "virtual" / "legacy")}"')
        gamecommand = gamecommand.replace("${assets_index_name}", f'"{assets}"')
        gamecommand = gamecommand.replace("${auth_uuid}", f'"{player_uuid}"')
        gamecommand = gamecommand.replace("${auth_access_token}", f'"{player_access_token}"')
        # c = c.replace("${clientid}", "${clientid}")
        # c = c.replace("${auth_xuid}", "${auth_xuid}")
        gamecommand = gamecommand.replace("${player_accountType}", f'"{player_type}"')
        gamecommand = gamecommand.replace("${version_type}", f'"{version_type}"')
        if extra_game_command:
            gamecommand = gamecommand.split(" ")
            gamecommand.append(extra_game_command.strip(" "))
            gamecommand = " ".join(gamecommand)
        jvmcommand = f"{' '.join(jvmcommand)} -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump -Djava.library.path=\"{str(Path(minecraft_path / 'versions' / version_launch / f'{version_launch}-natives'))}\" -cp \"{libraries_files}{':' if get_os.getOperationSystemName()[0] != 'Windows' else ';'}{game_jar_path}\" {memory_args} -Xmixed {main_class}"
    else:
        jvmcommand = gamecommand = ""
    command = f'"{java_path.strip(chr(34))}" {jvmcommand} {gamecommand}'
    return command


def launch(
        minecraft_path=None,
        version_launch=None,
        java_path=None,
        launch_mode="client",
        launcher_version="",
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
            java_path = get_java_path(str(i))
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
    command = generate_launch_command(minecraft_path, java_path, version_launch, player_data, launch_mode,
                                      jvm_arg_options, extra_game_command, quickplay_command, initial_memory,
                                      max_memory, launcher_version)
    print(command)
    unpack_natives_files(minecraft_path, version_launch)
    game = subprocess.Popen(
        shlex.split(command),
        stdout=stdout,
        stderr=stderr,
        creationflags=subprocess.CREATE_NO_WINDOW,
        cwd=str(minecraft_path)
    )
    # print(detect(output), output.decode(detect(output)['encoding']))
    return "Successfully", game


def analysis_log(output, error=None):
    # r"[\u4e00-\u9fa5]"
    search = re.search(r"#@!@#", output, re.I)
    if error:
        search1 = re.search(r"#@!@#", error, re.I)
    else:
        search1 = None
    if search is not None or search1 is not None:
        data = re.split(r"#@!@#", output if search is not None else error)[-1]
        file = Path(data.strip())
        report = file.read_text(encoding="utf-8").split("\n")
        for i in report:
            if "Description: " in i:
                description = i.split(":")[-1].strip()
                reason = report_description_lists.get(description, description)
                # q.Put(("Error:", reason))
                return "Error:", reason
