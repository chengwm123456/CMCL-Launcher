# -*- coding: utf-8 -*-
import json
import os
from typing import *
from pathlib import Path, PurePath
import shlex

from CMCLCore.CMCLDefines import Player, Minecraft
from CMCLCore.Player import AuthlibInjectorPlayer
from CMCLCore import GetOperationSystem

from .TemplateFilling import MinecraftArgumentTemplateFilling, JVMArgumentTemplateFilling


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
    mcAssetsIndex = mcJsonFile.get("assets")
    mcMainClass = mcJsonFile.get("mainClass")
    mcVersionType = mcJsonFile.get("type")
    mcLibrariesFileDatas = mcJsonFile.get("libraries", [])
    mcLibrariesFiles = []
    mcLibrariesFilesNames = {}
    for mcLib in mcLibrariesFileDatas:
        if mcLib.get("downloads"):
            if mcLib.get("rules"):
                action = "disallow"
                for rule in mcLib.get("rules", []):
                    ruleOfOs = rule.get("os", {}).get("name", GetOperationSystem.GetOperationSystemInMojangApi()[0])
                    if ruleOfOs != GetOperationSystem.GetOperationSystemInMojangApi()[0]:
                        continue
                    action = rule.get("action", action)
                allow = bool(mcLib.get("downloads", {}).get("artifact", {})) and action == "allow"
            else:
                allow = bool(mcLib.get("downloads", {}).get("artifact", {}))
            downloads = mcLib.get("downloads", {})
            if downloads.get("artifact") and allow:
                mcLibJarNames = mcLib.get("name", "::").split(":")
                mcLibJarFile = PurePath(f"{'-'.join(mcLibJarNames[1:])}.jar")
                mcLibPath = Path(
                    Path(mcLibJarNames[0].replace(".", os.sep)) / mcLibJarNames[1] / mcLibJarNames[
                        2] / mcLibJarFile)
                mc_lib_path_artifact = Path(minecraft.mc_gameLibrariesDir / mcLibPath)
                if len(mcLibJarNames) > 3:
                    mc_lib_name_id = tuple(mcLibJarNames[:-2] + [mcLibJarNames[-1]])
                else:
                    mc_lib_name_id = tuple(mcLibJarNames[:2])
                if mc_lib_name_id in mcLibrariesFilesNames:
                    mcLibrariesFiles[mcLibrariesFilesNames[mc_lib_name_id]] = str(mc_lib_path_artifact)
                else:
                    mcLibrariesFiles.append(str(mc_lib_path_artifact))
                mcLibrariesFilesNames[mc_lib_name_id] = len(mcLibrariesFiles) - 1
        else:
            mcLibJarNames = mcLib.get("name", ":::").split(":")
            mcLibJarFile = PurePath(" .jar").with_stem("-".join(mcLibJarNames[1:]))
            mcLibPath = Path(
                Path(mcLibJarNames[0].replace(".", os.sep)) / mcLibJarNames[1] / mcLibJarNames[
                    2] / mcLibJarFile)
            mc_lib_path_artifact = Path(minecraft.mc_gameLibrariesDir / mcLibPath)
            if len(mcLibJarNames) > 3:
                mc_lib_name_id = tuple(mcLibJarNames[:-2] + [mcLibJarNames[-1]])
            else:
                mc_lib_name_id = tuple(mcLibJarNames[:2])
            if mc_lib_name_id in mcLibrariesFilesNames:
                mcLibrariesFiles[mcLibrariesFilesNames[mc_lib_name_id]] = str(mc_lib_path_artifact)
            else:
                mcLibrariesFiles.append(str(mc_lib_path_artifact))
            mcLibrariesFilesNames[mc_lib_name_id] = len(mcLibrariesFiles) - 1
    mcLibrariesFiles = os.pathsep.join(mcLibrariesFiles)
    memory_args = f"-Xmn{str(initial_memory)} -Xmx{str(max_memory)}"
    if not jvm_arguments:
        jvm_arguments = []
    if isinstance(jvm_arguments, str):
        jvm_arguments = shlex.split(jvm_arguments)
    mc_jvm_command = jvm_arguments
    if mcJsonFile.get("arguments"):
        quick_started = False
        mcArguments = mcJsonFile["arguments"]
        mcGameArguments = mcArguments["game"]
        mcGameCommand = []
        for gameArgument in mcGameArguments:
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
                                mcGameCommand.append(quickplay_command)
                                continue
                            else:
                                if value[0] in ["--quickPlaySingleplayer",
                                                "--quickPlayMultiplayer",
                                                "--quickPlayRealms"]:
                                    continue
                                str_arg = str_arg.replace("${resolution_width}", "854")
                                str_arg = str_arg.replace("${resolution_height}", "480")
                                mcGameCommand.append(str_arg)
                    else:
                        str_arg = value
                        str_arg = str_arg.replace("${resolution_width}", "854")
                        str_arg = str_arg.replace("${resolution_height}", "480")
                        mcGameCommand.append(str_arg)
            else:
                mcGameCommand.append(
                    MinecraftArgumentTemplateFilling(gameArgument, player_data, minecraft, minecraftPath, mcAssetsIndex,
                                                     False,
                                                     mcVersionType))
        if extra_game_command:
            mcGameCommand.append(extra_game_command.strip(" "))
        mcGameCommand = " ".join(mcGameCommand)
        mc_jvm_arguments = mcArguments.get("jvm", [])
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
                                          f'"{mcLibrariesFiles}{os.pathsep}{mcGameJarFile}"')
                mc_jvm_command.append(str_arg)
        mc_jvm_command.append(memory_args)
        mc_jvm_command.append(
            f"-Xmixed {mcMainClass}")
        mc_jvm_command = " ".join(mc_jvm_command)
    elif mcJsonFile.get("minecraftArguments"):
        mcGameCommand = mcJsonFile["minecraftArguments"]
        mcGameCommand = MinecraftArgumentTemplateFilling(mcGameCommand, player_data, minecraft, minecraftPath,
                                                         mcAssetsIndex, True, mcVersionType)
        if extra_game_command:
            mcGameCommand = shlex.split(mcGameCommand)
            mcGameCommand.append(extra_game_command.strip(" "))
            mcGameCommand = " ".join(mcGameCommand)
        mc_jvm_command = f"{' '.join(mc_jvm_command)}{' -XstartOnFirstThread' if GetOperationSystem.GetOperationSystemInMojangApi()[0] == 'osx' else ''}{' -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump' if GetOperationSystem.GetOperationSystemInMojangApi()[0] == 'windows' else ''}{' -Xss1M' if GetOperationSystem.GetOperationSystemInMojangApi() == ('windows', 'x86') else ''} -Djava.library.path=\"{str(minecraft.mc_gameNativesDir)}\" -cp \"{mcLibrariesFiles}{':' if GetOperationSystem.GetOperationSystemName()[0] != 'Windows' else ';'}{mcGameJarFile}\" {memory_args} -Xmixed {mcMainClass}"
    else:
        mc_jvm_command = mcGameCommand = ""
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
    command = [f'"{java_path.strip(chr(34))}"', mc_jvm_command, mcGameCommand]
    return " ".join(command)
