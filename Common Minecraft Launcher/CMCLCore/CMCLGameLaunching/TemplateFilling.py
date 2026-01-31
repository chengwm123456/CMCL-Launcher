# -*- coding: utf-8 -*-
from typing import *
import shlex
import os
from pathlib import Path
from string import Template

from ..CMCLDefines import Player, Minecraft


def Quote(string: str) -> str:
    string = str(string)
    quotedString = shlex.quote(string)
    if quotedString[0] == quotedString[-1] == "'":
        quotedString = quotedString[1:-1]
    return f'"{quotedString}"'


def JVMArgumentTemplateFilling(
        argument: str,
        minecraft: Minecraft,
        launcherName: str,
        launcherVersion: str,
        librariesList: str
) -> str:
    variables = {
        "natives_directory": Quote(minecraft.mc_gameNativesDir),
        "launcher_name": Quote(launcherName),
        "launcher_version": Quote(launcherVersion),
        "classpath": Quote(f"{librariesList}{os.pathsep}{minecraft.mc_gameJarFile}")
    }
    return Template(argument).safe_substitute(variables)


def MinecraftArgumentTemplateFilling(
        argument: str,
        player: Player,
        minecraft: Minecraft,
        assetsIndex: str,
        versionType: str = "release"
) -> str:
    variables = {
        "auth_player_name": Quote(player.player_playerName),
        "version_name": Quote(minecraft.mc_gameVersion),
        "game_directory": Quote(minecraft.mc_gamePlayDir),
        "assets_root": Quote(minecraft.mc_gameAssetsDir),
        "game_assets": Quote(minecraft.mc_gameAssetsDir),
        "assets_index_name": Quote(assetsIndex),
        "auth_uuid": Quote(player.player_playerUUID),
        "auth_access_token": Quote(player.player_accessToken),
        "auth_session": Quote(player.player_accessToken),
        "clientid": "${clientid}",
        "auth_xuid": "${auth_xuid}",
        "user_type": Quote(player.player_accountType[1]),
        "version_type": Quote(versionType)
    }
    return Template(argument).safe_substitute(variables)
