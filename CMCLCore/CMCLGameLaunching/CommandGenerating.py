# -*- coding: utf-8 -*-
import json
import os
from typing import *
from pathlib import Path, PurePath
import shlex

from CMCLCore.CMCLDefines import Minecraft
from CMCLCore.CMCLDefines import Player
from CMCLCore.Player import AuthlibInjectorPlayer
from CMCLCore import GetOperationSystem


def GenerateMinecraftLaunchCommand(
        java_path: Union[str, Path, PurePath, os.PathLike, LiteralString],
        minecraft: Minecraft,
        player_data: Player,
        jvm_arguments: Optional[Union[str, list]],
        extra_game_command: str,
        quickplay_command: str,
        initial_memory: int,
        max_memory: int,
        launcher_name: str,
        launcher_version: str,
) -> str:
    minecraftPath = Path(minecraft.mc_gameWorkDir).absolute()
    mcJsonFile = json.loads(Path(minecraft.mc_gameJsonFile).read_text(encoding="utf-8"))
    mcGameJarFile = minecraft.mc_gameJarFile
    assets = mcJsonFile.get("assets")
    main_class = mcJsonFile.get("mainClass")
    version_type = mcJsonFile.get("type")
    mc_libraries_file_datas = mcJsonFile.get("libraries", [])
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
            if downloads.get("artifact") and allow:
                mc_lib_jar_names = mc_lib.get("name", ":::").split(":")
                mc_lib_jar_file = PurePath(" .jar").with_stem("-".join(mc_lib_jar_names[1:]))
                mc_lib_path = Path(
                    Path(mc_lib_jar_names[0].replace(".", os.sep)) / mc_lib_jar_names[1] / mc_lib_jar_names[
                        2] / mc_lib_jar_file)
                mc_lib_path_artifact = Path(minecraft.mc_gameLibrariesDir / mc_lib_path)
                if len(mc_lib_jar_names) > 3:
                    mc_lib_name_id = tuple(mc_lib_jar_names[:-2] + [mc_lib_jar_names[-1]])
                else:
                    mc_lib_name_id = tuple(mc_lib_jar_names[:2])
                if mc_lib_name_id in mc_libraries_files_names:
                    mc_libraries_files[mc_libraries_files_names[mc_lib_name_id]] = str(mc_lib_path_artifact)
                else:
                    mc_libraries_files.append(str(mc_lib_path_artifact))
                mc_libraries_files_names[mc_lib_name_id] = len(mc_libraries_files) - 1
        else:
            mc_lib_jar_names = mc_lib.get("name", ":::").split(":")
            mc_lib_jar_file = PurePath(" .jar").with_stem("-".join(mc_lib_jar_names[1:]))
            mc_lib_path = Path(
                Path(mc_lib_jar_names[0].replace(".", os.sep)) / mc_lib_jar_names[1] / mc_lib_jar_names[
                    2] / mc_lib_jar_file)
            mc_lib_path_artifact = Path(minecraft.mc_gameLibrariesDir / mc_lib_path)
            if len(mc_lib_jar_names) > 3:
                mc_lib_name_id = tuple(mc_lib_jar_names[:-2] + [mc_lib_jar_names[-1]])
            else:
                mc_lib_name_id = tuple(mc_lib_jar_names[:2])
            if mc_lib_name_id in mc_libraries_files_names:
                mc_libraries_files[mc_libraries_files_names[mc_lib_name_id]] = str(mc_lib_path_artifact)
            else:
                mc_libraries_files.append(str(mc_lib_path_artifact))
            mc_libraries_files_names[mc_lib_name_id] = len(mc_libraries_files) - 1
    mc_libraries_files = os.pathsep.join(mc_libraries_files)
    memory_args = f"-Xmn{str(initial_memory)} -Xmx{str(max_memory)}"
    if not jvm_arguments:
        jvm_arguments = []
    if isinstance(jvm_arguments, str):
        jvm_arguments = shlex.split(jvm_arguments)
    mc_jvm_command = jvm_arguments
    if mcJsonFile.get("arguments"):
        quick_started = False
        mc_arguments = mcJsonFile["arguments"]
        mc_game_arguments = mc_arguments["game"]
        mc_game_command = []
        for gameArgument in mc_game_arguments:
            if isinstance(gameArgument, dict):
                if gameArgument.get("value") == "--demo" and player_data.player_hasMC:
                    continue
                rules = gameArgument.get("rules", [{}])[0]
                value = gameArgument.get("value", "")
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
                mc_game_command.append(
                    MinecraftArgumentTemplateFilling(gameArgument, player_data, minecraft, minecraftPath, assets,
                                                     version_type))
        if extra_game_command:
            mc_game_command.append(extra_game_command.strip(" "))
        mc_game_command = " ".join(mc_game_command)
        mc_jvm_arguments = mc_arguments.get("jvm", [])
        for jvmArgument in mc_jvm_arguments:
            if isinstance(jvmArgument, dict):
                rules = jvmArgument["rules"][0]
                os_data = GetOperationSystem.GetOperationSystemInMojangApi()
                os_rules = rules["os"]
                if os_rules.get("name") and os_rules["name"] != os_data[0]:
                    continue
                if os_rules.get("arch") and os_data[1] != os_rules["arch"]:
                    continue
                value = jvmArgument["value"]
                if isinstance(value, list):
                    for one_val in value:
                        if " " in one_val and '"' not in one_val:
                            one_val = f'"{shlex.quote(one_val)[1:-1]}"'
                        mc_jvm_command.append(one_val)
                else:
                    mc_jvm_command.append(value)
            else:
                str_arg = jvmArgument
                if " " in str_arg:
                    str_arg = f'"{shlex.quote(str_arg)[1:-1]}"'
                str_arg = str_arg.replace("${natives_directory}", f'"{minecraft.mc_gameNativesDir}"')
                str_arg = str_arg.replace("${launcher_name}", f'"{launcher_name}"')
                str_arg = str_arg.replace("${launcher_version}", f'"{launcher_version}"')
                str_arg = str_arg.replace("${classpath}",
                                          f'"{mc_libraries_files}{os.pathsep}{mcGameJarFile}"')
                mc_jvm_command.append(str_arg)
        mc_jvm_command.append(memory_args)
        mc_jvm_command.append(
            f"-Xmixed {main_class}")
        mc_jvm_command = " ".join(mc_jvm_command)
    elif mcJsonFile.get("minecraftArguments"):
        mc_game_command = mcJsonFile["minecraftArguments"]
        mc_game_command = mc_game_command.replace("${auth_session}", f'"{player_data.player_accessToken}"')
        mc_game_command = mc_game_command.replace("${auth_player_name}", f'"{player_data.player_name}"')
        mc_game_command = mc_game_command.replace("${version_name}", f'"{minecraft.mc_gameVersion}"')
        mc_game_command = mc_game_command.replace("${game_directory}", f'"{minecraftPath}"')
        mc_game_command = mc_game_command.replace("${assets_root}",
                                                  f'"{Path(minecraft.mc_gameAssetsDir / "virtual" / "legacy")}"')
        mc_game_command = mc_game_command.replace("${game_assets}",
                                                  f'"{Path(minecraft.mc_gameAssetsDir / "virtual" / "legacy")}"')
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
        mc_jvm_command = f"{' '.join(mc_jvm_command)}{' -XstartOnFirstThread' if GetOperationSystem.GetOperationSystemInMojangApi()[0] == 'osx' else ''}{' -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump' if GetOperationSystem.GetOperationSystemInMojangApi()[0] == 'windows' else ''}{' -Xss1M' if GetOperationSystem.GetOperationSystemInMojangApi() == ('windows', 'x86') else ''} -Djava.library.path=\"{str(minecraft.mc_gameNativesDir)}\" -cp \"{mc_libraries_files}{':' if GetOperationSystem.GetOperationSystemName()[0] != 'Windows' else ';'}{mcGameJarFile}\" {memory_args} -Xmixed {main_class}"
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
    mc_jvm_command = mc_authlib_injector_command + mc_jvm_command
    command = [f'"{java_path.strip(chr(34))}"', mc_jvm_command, mc_game_command]
    return " ".join(command)


def JVMArgumentTemplateFilling(argument):
    pass


def MinecraftArgumentTemplateFilling(argument, player_data, minecraft, minecraft_path, assets_index,
                                     version_type="release"):
    argument = argument.replace("${auth_player_name}", f'"{player_data.player_name}"')
    argument = argument.replace("${version_name}", f'"{minecraft.mc_gameVersion}"')
    argument = argument.replace("${game_directory}", f'"{minecraft_path}"')
    argument = argument.replace("${assets_root}", f'"{minecraft.mc_gameAssetsDir}"')
    argument = argument.replace("${assets_index_name}", f'"{assets_index}"')
    argument = argument.replace("${auth_uuid}", f'"{player_data.player_uuid}"')
    argument = argument.replace("${auth_access_token}", f'"{player_data.player_accessToken}"')
    argument = argument.replace("${clientid}", f"${{clientid}}")
    argument = argument.replace("${auth_xuid}", f"${{auth_xuid}}")
    argument = argument.replace("${user_type}", f'"{player_data.player_accountType[1]}"')
    argument = argument.replace("${version_type}", f'"{version_type}"')
    return argument
