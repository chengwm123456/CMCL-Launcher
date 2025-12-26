# -*- coding: utf-8 -*-
import requests


def GetPlayerProfile(accessToken):
    response = requests.get(
        "https://api.minecraftservices.com/minecraft/profile",
        headers={"Authorization": f"Bearer {accessToken}"}
    )
    response.raise_for_status()
    return response.json()


def CheckPlayerNameAvailability(accessToken, name):
    response = requests.get(
        f"https://api.minecraftservices.com/minecraft/profile/name/{name}/available",
        headers={"Authorization": f"Bearer {accessToken}"}
    )
    response.raise_for_status()
    return response.json()["status"]


def PlayerNameChange(accessToken):
    response = requests.get(
        "https://api.minecraftservices.com/minecraft/profile/namechange",
        headers={"Authorization": f"Bearer {accessToken}"}
    )
    response.raise_for_status()
    return response.json()
