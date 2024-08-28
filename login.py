# -*- coding: utf-8 -*-
import logging

import requests

logging.basicConfig(
    level=logging.NOTSET,
    format="%(asctime)s[%(levelname)s]:%(message)s",
    datefmt="[%Y/%m/%d][%H:%M:%S %p]"
)


def get_user_data(token="", is_refresh_login=False):
    has_mc = False
    if is_refresh_login:
        params = {
            "client_id": "00000000402b5328",
            "refresh_token": token,
            "grant_type": "refresh_token",
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "scope": "service::user.auth.xboxlive.com::MBI_SSL"
        }
    else:
        params = {"client_id": "00000000402b5328",
                  "code": token,
                  "grant_type": "authorization_code",
                  "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
                  "scope": "service::user.auth.xboxlive.com::MBI_SSL"}
    response = requests.get(
        "https://login.live.com/oauth20_token.srf",
        params=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        verify=True
    )
    if response.json().get('player_accessToken', None) is not None:
        access_token_1 = response.json()['player_accessToken']
        refresh_token = response.json()['refresh_token']
    else:
        return "Unsuccessfully", None, None, None, None, False
    json_in_step_2 = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": access_token_1
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }
    response_2 = requests.post(
        "https://user.auth.xboxlive.com/user/authenticate",
        json=json_in_step_2,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        verify=True)
    xbl_token = response_2.json()["Token"]
    uhs = response_2.json()["DisplayClaims"]["xui"][0]["uhs"]
    json_in_step_3 = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                xbl_token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }
    response_3 = requests.post(
        "https://xsts.auth.xboxlive.com/xsts/authorize",
        json=json_in_step_3,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        verify=True
    )
    xsts_token = response_3.json()["Token"]
    uhs2 = response_3.json()["DisplayClaims"]["xui"][0]["uhs"]
    if uhs != uhs2:
        return "Unsuccessfully", None, None, None, None, False
    else:
        response_4 = requests.post(
            "https://api.minecraftservices.com/authentication/login_with_xbox",
            json={"identityToken": f"XBL3.0 x={uhs};{xsts_token}"},
            verify=True
        )
        minecraft_access_token = response_4.json()["player_accessToken"]
        response_profile = requests.get(
            "https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": f"Bearer {minecraft_access_token}"},
            verify=True
        )
        if response_profile.json().get("error", None) is None:
            uuid = response_profile.json()["id"]
            user_name = response_profile.json()["name"]
            response_mc = requests.get("https://api.minecraftservices.com/entitlements/mcstore",
                                       headers={"Authorization": f"Bearer {minecraft_access_token}"},
                                       verify=True
                                       )
            if not response_mc.text == "" and response_mc.text is not None:
                has_mc = True
            return "Successfully", user_name, uuid, minecraft_access_token, refresh_token, has_mc
