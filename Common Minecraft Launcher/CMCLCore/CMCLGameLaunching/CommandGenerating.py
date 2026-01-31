# -*- coding: utf-8 -*-
from typing import *

import os
import shlex
from pathlib import Path

from ..CMCLDefines import Player, Minecraft
from ..Player import AuthlibInjectorPlayer

from .TemplateFilling import Quote, MinecraftArgumentTemplateFilling, JVMArgumentTemplateFilling
from .LibrariesGenerating import GenerateMinecraftLibrariesFiles


def GenerateMinecraftLaunchCommand(
        javaPath: Union[str, os.PathLike[str], Path, LiteralString],
        minecraft: Minecraft,
        player: Player,
        jvmArguments: Optional[Union[str, list]],
        extraLaunchCommand: Optional[Union[str, list]],
        quickplayCommand: Union[str, LiteralString],
        initialMemory: int,
        maxMemory: int,
        launcherBrand: Union[str, LiteralString],
        launcherVersion: Union[str, LiteralString],
        **gameSettings
) -> Union[str, LiteralString]:
    mcJsonFile = minecraft.mc_gameJsonFileContent
    mcGameJarFile = minecraft.mc_gameJarFile
    mcAssetsIndex = mcJsonFile.get("assets")
    mcMainClass = mcJsonFile.get("mainClass")
    mcVersionType = mcJsonFile.get("type")
    mcLibrariesFileDatas = mcJsonFile.get("libraries")
    mcLibrariesFiles = os.pathsep.join(GenerateMinecraftLibrariesFiles(minecraft, mcLibrariesFileDatas))
    memory_args = f"-Xmn{str(initialMemory)} -Xmx{str(maxMemory)}"
    if not jvmArguments:
        jvmArguments = []
    if isinstance(jvmArguments, str):
        jvmArguments = shlex.split(jvmArguments)
    mcJVMCommand = jvmArguments
    if mcJsonFile.get("arguments"):
        quick_started = False
        mcArguments = mcJsonFile["arguments"]
        mcGameArguments = mcArguments["game"]
        mcGameCommand = []
        for gameArgument in mcGameArguments:
            if isinstance(gameArgument, dict):
                if gameArgument.get("value") == "--demo" and player.player_hasMC:
                    continue
                rules = gameArgument.get("rules", [{}])[0]
                value = gameArgument.get("value", "")
                features = rules.get("features", {})
                if features.values():
                    if isinstance(value, list):
                        for strArgument in value:
                            if value[0] in ["--quickPlaySingleplayer", "--quickPlayMultiplayer", "--quickPlayRealms"] \
                                    and not quick_started and quickplayCommand is not None:
                                quick_started = True
                                mcGameCommand.append(quickplayCommand)
                                continue
                            else:
                                if value[0] in ["--quickPlaySingleplayer",
                                                "--quickPlayMultiplayer",
                                                "--quickPlayRealms"]:
                                    continue
                                strArgument = strArgument.replace("${resolution_width}",
                                                                  str(gameSettings.get("resolution_width", 854)))
                                strArgument = strArgument.replace("${resolution_height}",
                                                                  str(gameSettings.get("resolution_width", 480)))
                                mcGameCommand.append(strArgument)
                    else:
                        strArgument = value
                        strArgument = strArgument.replace("${resolution_width}",
                                                          str(gameSettings.get("resolution_width", 854)))
                        strArgument = strArgument.replace("${resolution_height}",
                                                          str(gameSettings.get("resolution_width", 480)))
                        mcGameCommand.append(strArgument)
            else:
                mcGameCommand.append(
                    MinecraftArgumentTemplateFilling(
                        gameArgument,
                        player,
                        minecraft,
                        mcAssetsIndex,
                        mcVersionType
                    )
                )
        if extraLaunchCommand:
            if isinstance(extraLaunchCommand, str):
                mcGameCommand.append(extraLaunchCommand.strip(" "))
            else:
                mcGameCommand.extend(extraLaunchCommand)
        mcGameCommand = " ".join(mcGameCommand)
        mcJVMArguments = mcArguments.get("jvm", [])
        for jvmArgument in mcJVMArguments:
            if isinstance(jvmArgument, dict):
                rules = jvmArgument["rules"][0]
                ruleReqOS = rules["os"]
                if (ruleReqOS.get("name", minecraft.mc_gamePlatformName) != minecraft.mc_gamePlatformName
                        or ruleReqOS.get("arch", minecraft.mc_gamePlatformMachine) != minecraft.mc_gamePlatformMachine):
                    continue
                value = jvmArgument["value"]
                if isinstance(value, list):
                    value = list(map(
                        lambda val: Quote(val) if " " in val and '"' not in val else val, value))
                    mcJVMCommand.extend(value)
                else:
                    mcJVMCommand.append(value)
            else:
                strArgument = Quote(jvmArgument) if " " in jvmArgument and '"' not in jvmArgument else jvmArgument
                mcJVMCommand.append(
                    JVMArgumentTemplateFilling(
                        strArgument,
                        minecraft,
                        launcherBrand,
                        launcherVersion,
                        mcLibrariesFiles
                    )
                )
        mcJVMCommand.append(memory_args)
        mcJVMCommand.append(
            f"-Xmixed {mcMainClass}")
        mcJVMCommand = " ".join(mcJVMCommand)
    elif mcJsonFile.get("minecraftArguments"):
        mcGameCommand = MinecraftArgumentTemplateFilling(
            mcJsonFile["minecraftArguments"],
            player,
            minecraft,
            mcAssetsIndex,
            mcVersionType
        )
        if extraLaunchCommand:
            mcGameCommand = shlex.split(mcGameCommand)
            if isinstance(extraLaunchCommand, str):
                mcGameCommand.append(extraLaunchCommand.strip(" "))
            else:
                mcGameCommand.extend(extraLaunchCommand)
            mcGameCommand = " ".join(mcGameCommand)
        mcJVMCommand = f"{' '.join(mcJVMCommand)}{' -XstartOnFirstThread' if minecraft.mc_gamePlatformName == 'osx' else ''}{' -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump' if minecraft.mc_gamePlatformName == 'windows' else ''}{' -Xss1M' if (minecraft.mc_gamePlatformName, minecraft.mc_gamePlatformMachine) == ('windows', 'x86') else ''} -Djava.library.path=\"{str(minecraft.mc_gameNativesDir)}\" -cp \"{mcLibrariesFiles}{os.pathsep}{mcGameJarFile}\" {memory_args} -Xmixed {mcMainClass}"
    else:
        mcJVMCommand = mcGameCommand = ""
    if isinstance(player, AuthlibInjectorPlayer):
        authlibInjectorJarPath = (player.player_authlibInjectorPath or Path("./authlib-injector.jar")).absolute()
        authenticationServerUrl = player.player_authServer  # "https://littleskin.cn/api/yggdrasil"
        signaturePublickey = player.player_signaturePublickey.replace("\n", "")
        mcAuthlibInjectorCommand = " ".join(
            [
                f'-javaagent:{Quote(str(authlibInjectorJarPath))}={Quote(authenticationServerUrl)}',
                '-Dauthlibinjector.side="client"',
                f'-Dauthlibinjector.yggdrasil.prefetched={Quote(signaturePublickey)}'
            ]
        ) + " "
    else:
        mcAuthlibInjectorCommand = ""
    mcJVMCommand = mcAuthlibInjectorCommand + mcJVMCommand
    command = f'"{javaPath.strip(chr(34))}"', mcJVMCommand, mcGameCommand
    return " ".join(command)
