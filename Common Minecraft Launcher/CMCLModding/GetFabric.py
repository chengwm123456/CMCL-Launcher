# -*- coding: utf-8 -*-
import requests

from .GetMods import ListModVersions


def GetGameVersions():
    response = requests.get("https://meta.fabricmc.net/v2/versions/game").json()
    return response


def GetFabricLoaderVersions():
    response = requests.get("https://meta.fabricmc.net/v2/versions/loader").json()
    return response


def GetFabricApiVersions(game_version=None):
    return ListModVersions("Fabric API", game_version=game_version)


def GetDownloadUrlBase(game, loader):
    return f"https://meta.fabricmc.net/v2/versions/loader/{game}/{loader}"
