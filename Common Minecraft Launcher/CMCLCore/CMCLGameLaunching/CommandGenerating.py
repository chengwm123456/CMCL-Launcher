# -*- coding: utf-8 -*-
import os
from typing import *
from pathlib import Path
import shlex

from ..CMCLDefines import Player, Minecraft
from ..Player import AuthlibInjectorPlayer
from .. import GetOperationSystem

from .TemplateFilling import Quote, MinecraftArgumentTemplateFilling, JVMArgumentTemplateFilling
from .LibrariesGenerating import GenerateMinecraftLibrariesFiles


def GenerateMinecraftLaunchCommand(
        java_path: Union[str, os.PathLike[str], Path, LiteralString],
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
    mcJsonFile = minecraft.mc_gameJsonFileContent
    mcGameJarFile = minecraft.mc_gameJarFile
    mcAssetsIndex = minecraft.mc_gameAssetsIndex
    mcMainClass = minecraft.mc_gameMainClass
    mcVersionType = mcJsonFile.get("type")
    mcLibrariesFileDatas = minecraft.mc_gameLibrariesFiles
    mcLibrariesFiles = os.pathsep.join(GenerateMinecraftLibrariesFiles(minecraft, mcLibrariesFileDatas))
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
                    MinecraftArgumentTemplateFilling(
                        gameArgument,
                        player_data,
                        minecraft,
                        mcAssetsIndex,
                        False,
                        mcVersionType
                    )
                )
        if extra_game_command:
            mcGameCommand.append(extra_game_command.strip(" "))
        mcGameCommand = " ".join(mcGameCommand)
        mcJvmArguments = mcArguments.get("jvm", [])
        for jvmArgument in mcJvmArguments:
            if isinstance(jvmArgument, dict):
                rules = jvmArgument["rules"][0]
                ruleOfOS = rules["os"]
                if ruleOfOS.get("name") and ruleOfOS["name"] != minecraft.mc_gamePlatformName:
                    continue
                if ruleOfOS.get("arch") and minecraft.mc_gamePlatformMachine != ruleOfOS["arch"]:
                    continue
                value = jvmArgument["value"]
                if isinstance(value, list):
                    for oneValue in value:
                        if " " in oneValue and '"' not in oneValue:
                            oneValue = Quote(oneValue)
                        mcJvmCommand.append(oneValue)
                else:
                    mcJvmCommand.append(value)
            else:
                strArgument = jvmArgument
                if " " in strArgument:
                    strArgument = Quote(strArgument)
                mcJvmCommand.append(
                    JVMArgumentTemplateFilling(
                        strArgument,
                        minecraft,
                        launcher_name,
                        launcher_version,
                        mcLibrariesFiles
                    )
                )
        mcJvmCommand.append(memory_args)
        mcJvmCommand.append(
            f"-Xmixed {mcMainClass}")
        mcJvmCommand = " ".join(mcJvmCommand)
    elif mcJsonFile.get("minecraftArguments"):
        mcGameCommand = MinecraftArgumentTemplateFilling(
            mcJsonFile["minecraftArguments"],
            player_data,
            minecraft,
            mcAssetsIndex,
            True,
            mcVersionType)
        if extra_game_command:
            mcGameCommand = shlex.split(mcGameCommand)
            mcGameCommand.append(extra_game_command.strip(" "))
            mcGameCommand = " ".join(mcGameCommand)
        mcJvmCommand = f"{' '.join(mcJvmCommand)}{' -XstartOnFirstThread' if GetOperationSystem.GetOperationSystemInMojangAPI()[0] == 'osx' else ''}{' -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump' if GetOperationSystem.GetOperationSystemInMojangAPI()[0] == 'windows' else ''}{' -Xss1M' if GetOperationSystem.GetOperationSystemInMojangAPI() == ('windows', 'x86') else ''} -Djava.library.path=\"{str(minecraft.mc_gameNativesDir)}\" -cp \"{mcLibrariesFiles}{':' if GetOperationSystem.GetOperationSystemName() != 'Windows' else ';'}{mcGameJarFile}\" {memory_args} -Xmixed {mcMainClass}"
    else:
        mcJvmCommand = mcGameCommand = ""
    if isinstance(player_data, AuthlibInjectorPlayer):
        authlibInjectorJarPath = (player_data.player_authlibInjectorPath or Path("./authlib-injector.jar")).absolute()
        authenticationServerUrl = player_data.player_authServer  # "https://littleskin.cn/api/yggdrasil"
        signaturePublickey = player_data.player_signaturePublickey.replace("\n", "")
        mcAuthlibInjectorCommand = " ".join(
            [
                f'-javaagent:"{Quote(str(authlibInjectorJarPath))}"="{Quote(authenticationServerUrl)}"',
                '-Dauthlibinjector.side="client"',
                f'-Dauthlibinjector.yggdrasil.prefetched="{Quote(signaturePublickey)}"'
            ]
        )
    else:
        mcAuthlibInjectorCommand = ""
    mcJvmCommand = mcAuthlibInjectorCommand + mcJvmCommand
    command = [f'"{java_path.strip(chr(34))}"', mcJvmCommand, mcGameCommand]
    return " ".join(command)
