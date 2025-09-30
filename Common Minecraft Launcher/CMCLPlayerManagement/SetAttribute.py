# -*- coding: utf-8 -*-
import requests


def ChangePlayerName(accessToken, name):
    response = requests.put(
        f"https://api.minecraftservices.com/minecraft/profile/name/{name}",
        headers={"Authorization": f"Bearer {accessToken}"}
    )
    response.raise_for_status()
    return response.json()


def UploadPlayerSkin(accessToken, skinVariant, fileContent):
    response = requests.post(
        "https://api.minecraftservices.com/minecraft/profile/skins",
        headers={"Authorization": f"Bearer {accessToken}"},
        json={
            "variant": skinVariant or "classic",
            "file": fileContent
        }
    )
    response.raise_for_status()
