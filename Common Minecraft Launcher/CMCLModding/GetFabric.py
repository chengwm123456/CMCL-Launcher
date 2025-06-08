# -*- coding: utf-8 -*-
import requests


def GetGameVersions():
    response = requests.get("https://meta.fabricmc.net/v2/versions").json()
    return response["game"]


def GetFabricLoaderVersions():
    response = requests.get("https://meta.fabricmc.net/v2/versions").json()
    return response["loaders"]


def GetDownloadUrlBase(game, loader):
    return f"https://meta.fabricmc.net/v2/versions/loader/{game}/{loader}"
