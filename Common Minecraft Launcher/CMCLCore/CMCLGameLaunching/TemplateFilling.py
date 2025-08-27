# -*- coding: utf-8 -*-
from typing import *
import shlex
import os
from pathlib import Path

from ..CMCLDefines import Player, Minecraft


def Quote(string: str) -> str:
    quotedString = shlex.quote(string)
    if (quotedString[0], quotedString[-1]) == ("'", "'"):
        quotedString = quotedString[1:-1]
    return f'"{quotedString}"'


def JVMArgumentTemplateFilling(
        argument: str,
        minecraft: Minecraft,
        launcherName: str,
        launcherVersion: str,
        librariesList: str
) -> str:
    argument = argument.replace("${natives_directory}", f'"{minecraft.mc_gameNativesDir}"')
    argument = argument.replace("${launcher_name}", f'"{launcherName}"')
    argument = argument.replace("${launcher_version}", f'"{launcherVersion}"')
    argument = argument.replace("${classpath}", f'"{librariesList}{os.pathsep}{minecraft.mc_gameJarFile}"')
    return argument


def MinecraftArgumentTemplateFilling(
        argument: str,
        player: Player,
        minecraft: Minecraft,
        assetsIndex: str,
        versionType: str = "release"
) -> str:
    argument = argument.replace("${auth_player_name}", f'"{player.player_playerName}"')
    argument = argument.replace("${version_name}", f'"{minecraft.mc_gameVersion}"')
    argument = argument.replace("${game_directory}", f'"{minecraft.mc_gamePlayDir}"')
    argument = argument.replace(
        "${assets_root}", f'"{minecraft.mc_gameAssetsDir}"').replace("${game_assets}",
                                                                     f'"{minecraft.mc_gameAssetsDir}"')
    argument = argument.replace("${assets_index_name}", f'"{assetsIndex}"')
    argument = argument.replace("${auth_uuid}", f'"{player.player_playerUUID}"')
    argument = argument.replace("${auth_access_token}", f'"{player.player_accessToken}"').replace(
        "${auth_session}", f'"{player.player_accessToken}"').replace(
        "${auth_access_token}", f'"{player.player_accessToken}"')
    argument = argument.replace("${clientid}", f"${{clientid}}")
    argument = argument.replace("${auth_xuid}", f"${{auth_xuid}}")
    argument = argument.replace("${user_type}", f'"{player.player_accountType[1]}"')
    argument = argument.replace("${version_type}", f'"{versionType}"')
    return argument
