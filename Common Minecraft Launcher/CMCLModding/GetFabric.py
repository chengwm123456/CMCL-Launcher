# -*- coding: utf-8 -*-
import requests

from .GetMods import ListModVersions


def GetGameVersions():
    response = requests.get("https://meta.fabricmc.net/v2/versions/game").json()
    return response


def GetFabricLoaderVersions():
    response = requests.get("https://meta.fabricmc.net/v2/versions/loader").json()
    return response


def GetFabricApiVersions():
    return ListModVersions("Fabric API")


def GetDownloadUrlBase(game, loader):
    return f"https://meta.fabricmc.net/v2/versions/loader/{game}/{loader}"
