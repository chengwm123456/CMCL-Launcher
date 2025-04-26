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
    mcJvmCommand = jvm_arguments
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
                        for strArgument in value:
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
                                strArgument = strArgument.replace("${resolution_width}", "854")
                                strArgument = strArgument.replace("${resolution_height}", "480")
                                mcGameCommand.append(strArgument)
                    else:
                        strArgument = value
                        strArgument = strArgument.replace("${resolution_width}", "854")
                        strArgument = strArgument.replace("${resolution_height}", "480")
                        mcGameCommand.append(strArgument)
            else:
                mcGameCommand.append(
                    MinecraftArgumentTemplateFilling(gameArgument, player_data, minecraft, minecraftPath, mcAssetsIndex,
                                                     False,
                                                     mcVersionType))
        if extra_game_command:
            mcGameCommand.append(extra_game_command.strip(" "))
        mcGameCommand = " ".join(mcGameCommand)
        mcJvmArguments = mcArguments.get("jvm", [])
        for jvmArgument in mcJvmArguments:
            if isinstance(jvmArgument, dict):
                rules = jvmArgument["rules"][0]
                currentOs = GetOperationSystem.GetOperationSystemInMojangApi()
                ruleOfOs = rules["os"]
                if ruleOfOs.get("name") and ruleOfOs["name"] != currentOs[0]:
                    continue
                if ruleOfOs.get("arch") and currentOs[1] != ruleOfOs["arch"]:
                    continue
                value = jvmArgument["value"]
                if isinstance(value, list):
                    for oneValue in value:
                        if " " in oneValue and '"' not in oneValue:
                            oneValue = f'"{shlex.quote(oneValue)[1:-1]}"'
                        mcJvmCommand.append(oneValue)
                else:
                    mcJvmCommand.append(value)
            else:
                strArgument = jvmArgument
                if " " in strArgument:
                    strArgument = f'"{shlex.quote(strArgument)[1:-1]}"'
                strArgument = strArgument.replace("${natives_directory}", f'"{minecraft.mc_gameNativesDir}"')
                strArgument = strArgument.replace("${launcher_name}", f'"{launcher_name}"')
                strArgument = strArgument.replace("${launcher_version}", f'"{launcher_version}"')
                strArgument = strArgument.replace("${classpath}",
                                                  f'"{mcLibrariesFiles}{os.pathsep}{mcGameJarFile}"')
                mcJvmCommand.append(strArgument)
        mcJvmCommand.append(memory_args)
        mcJvmCommand.append(
            f"-Xmixed {mcMainClass}")
        mcJvmCommand = " ".join(mcJvmCommand)
    elif mcJsonFile.get("minecraftArguments"):
        mcGameCommand = mcJsonFile["minecraftArguments"]
        mcGameCommand = MinecraftArgumentTemplateFilling(mcGameCommand, player_data, minecraft, minecraftPath,
                                                         mcAssetsIndex, True, mcVersionType)
        if extra_game_command:
            mcGameCommand = shlex.split(mcGameCommand)
            mcGameCommand.append(extra_game_command.strip(" "))
            mcGameCommand = " ".join(mcGameCommand)
        mcJvmCommand = f"{' '.join(mcJvmCommand)}{' -XstartOnFirstThread' if GetOperationSystem.GetOperationSystemInMojangApi()[0] == 'osx' else ''}{' -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump' if GetOperationSystem.GetOperationSystemInMojangApi()[0] == 'windows' else ''}{' -Xss1M' if GetOperationSystem.GetOperationSystemInMojangApi() == ('windows', 'x86') else ''} -Djava.library.path=\"{str(minecraft.mc_gameNativesDir)}\" -cp \"{mcLibrariesFiles}{':' if GetOperationSystem.GetOperationSystemName()[0] != 'Windows' else ';'}{mcGameJarFile}\" {memory_args} -Xmixed {mcMainClass}"
    else:
        mcJvmCommand = mcGameCommand = ""
    if isinstance(player_data, AuthlibInjectorPlayer):
        authlibInjectorJarPath = Path(r".\authlib-injector.jar")
        authenticationServerUrl = player_data.player_authServer  # "https://littleskin.cn/api/yggdrasil"
        signaturePublickey = player_data.player_signaturePublickey.replace("\n", "")
        mcAuthlibInjectorCommand = " ".join(
            [
                f'-javaagent:"{shlex.quote(str(authlibInjectorJarPath)[1:-1])}"="{shlex.quote(authenticationServerUrl)[1:-1]}"',
                '-Dauthlibinjector.side="client"',
                f'-Dauthlibinjector.yggdrasil.prefetched="{shlex.quote(signaturePublickey)[1:-1]}"'
            ]
        )
    else:
        mcAuthlibInjectorCommand = ""
    mcJvmCommand = mcAuthlibInjectorCommand + mcJvmCommand
    command = [f'"{java_path.strip(chr(34))}"', mcJvmCommand, mcGameCommand]
    return " ".join(command)
