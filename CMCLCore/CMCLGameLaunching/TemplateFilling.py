# -*- coding: utf-8 -*-
from typing import *
import shlex
import os
from pathlib import Path, PurePath

from CMCLCore.CMCLDefines import Player, Minecraft


def Quote(argument: str):
    return f'"{shlex.quote(argument)[1:-1]}"'


def JVMArgumentTemplateFilling(
        argument: str,
        minecraft: Minecraft,
        launcher_name: str,
        launcher_version: str,
        libraries_list: str
):
    argument = argument.replace("${natives_directory}", f'"{minecraft.mc_gameNativesDir}"')
    argument = argument.replace("${launcher_name}", f'"{launcher_name}"')
    argument = argument.replace("${launcher_version}", f'"{launcher_version}"')
    argument = argument.replace("${classpath}", f'"{libraries_list}{os.pathsep}{minecraft.mc_gameJarFile}"')
    return argument


def MinecraftArgumentTemplateFilling(
        argument: str,
        player_data: Player,
        minecraft: Minecraft,
        assets_index: str,
        assets_legacy: bool = False,
        version_type: str = "release"
):
    argument = argument.replace("${auth_player_name}", f'"{player_data.player_playerName}"')
    argument = argument.replace("${version_name}", f'"{minecraft.mc_gameVersion}"')
    argument = argument.replace("${game_directory}", f'"{minecraft.mc_gameWorkDir}"')
    if assets_legacy:
        gameAssetsDir = PurePath(minecraft.mc_gameAssetsDir) / "virtual" / "legacy"
    else:
        gameAssetsDir = PurePath(minecraft.mc_gameAssetsDir)
    argument = argument.replace("${assets_root}", f'"{gameAssetsDir}"').replace("${game_assets}",
                                                                                f'"{Path(gameAssetsDir)}"')
    argument = argument.replace("${assets_index_name}", f'"{assets_index}"')
    argument = argument.replace("${auth_uuid}", f'"{player_data.player_playerUUID}"')
    argument = argument.replace("${auth_access_token}", f'"{player_data.player_accessToken}"').replace(
        "${auth_session}", f'"{player_data.player_accessToken}"').replace("${auth_access_token}",
                                                                          f'"{player_data.player_accessToken}"')
    argument = argument.replace("${clientid}", f"${{clientid}}")
    argument = argument.replace("${auth_xuid}", f"${{auth_xuid}}")
    argument = argument.replace("${user_type}", f'"{player_data.player_accountType[1]}"')
    argument = argument.replace("${version_type}", f'"{version_type}"')
    return argument
