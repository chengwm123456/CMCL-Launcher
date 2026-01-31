# -*- coding: utf-8 -*-
import requests


def GetNeoForgeVersions():
    response = requests.get("https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge").json()
    return response
#
#
# def GetDownloadUrl(loader):
#     return f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{loader}/neoforge-{loader}-installer.jar"
