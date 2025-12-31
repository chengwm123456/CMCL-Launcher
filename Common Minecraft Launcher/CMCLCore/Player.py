# -*- coding: utf-8 -*-
from typing import *

import os
import uuid
import jwt
import random
import time
from pathlib import Path
from .CMCLDefines.Player import Player
from enum import Enum

secret_key = b'R\x06\r\xec\xfc\xcb\xf2\x0f\t\xf0\x06\x19U\x88\t.\xfb\xe6\xc62\xcc>\xc9\x13\'D}\xe8\x02cN\x109\xe7\x9b}\xc46y\xcf&\xaf#uwq\xf0"\x0f\xaa\xaa\x92"?\xa0\xfd\x11\xfcb\\d\x04\'S\x98\x89\x1f\xd6\xdeMn\xa0\x93\x0f,\x1e\x1b\xa4V\xa7\x80\xc4?\xd6;\xf8\x91\x15u\x9b\x15\x9f\xe1\xcd\xf5\x8a\xaf\xa8"\x16\xb35\xc6\xa0\xf1\xef\x1a\xcb\xba\xde7\x96N\x92\x8cH\t KG2\x11\xb6\xfa\x8e\xfa\xf1\x19\x8akg\xe2\xa1\x03R\xeai\\\x07\xb0\xbb#\x99\x00\x86\xd2\xb5\x9a\x00\xee\x13\xb4^\xc61|V\x8f\xf3K\x99\xb7"@\xd4uZ\xd2\xd56\xaa\xc8\x17,\xd9\x9b]\x04\xd0\x06L\xe5\x0b\xb9I1\xd8\x89\x08\xd9\x0c\x81K\x80\xec\x84)\x01\xb4\x13\x958\x1f\xb7K\xab{d\x856y\x02\xa6\x90\t\xda\xfe\xc6\xb7.\xedX\xf7\x1d\xd8\xa9$\xca\xd0?\xc9\x9cj\x0b\xaa\x8cU\xf8\x08\x86\x818\x9f\x15\xaf\xba2\xc7P\xfe\xf4z\x1f]\xc6\x9a\xe7\xebZ\'q\x11\xf1\xb88\xd2\xee\xdc!\xf90\x1d\xe8\x0c\x1aY\xd0I\x91\xef\xcbv\xc4\xd4\xf6/\xc2m\xe4Xj\x8d@\x88>\xec\xf9\x8f5k,\xdbl\xeb\xd0\xd8x\xfb1\xd2\xa2\x97`\xd2F\xe76\xc0^\xe5\xd0\x19b\xe5\x86\xb0x /p\x03a\x99\x92\xb9]\x80A\x1ao\xe2\'f\xc6_\x99\xd7.\xffj\x02\xfa+\xdd\xabi\xaa\xad=|\xf0\xd79\x94\xaek\xd1E\x8d\xf2\xe3\x16O\x9c\x97Rg\x7f\xb5\x7f\xce\xca#"\xef\\\x11ro\xad@\xff6\x8c\x07\xef|\xaf\xdc\x08\x81U\xa3\xfc\x9b\x7f\xb0\xcb\x1c\xc5\xc7\x91p!Nd\x98\xe3J\xb8\xf4\xcbg\xd7\xef]\xc5\xc9\xa2\x8c\x00\x91\xa2\xb8\xa8\xfa\xe8\x9b\xbex\tT\x92hTa!\xf6\xb4\xb0\x93Y\xc9\xfa4Y\x1c\xae)\x06T\x043\xce\t\x9a\xa03`\xd8\xaeX\xca\xed\xaeI*\xfe\n\x9f\x1d+\x85\x13\x8d\xe5m\x91\x83\x1fF!&\xa0\xf6\x01r\x1eD\x84\x8b\xccd\x17\xdd\x80\xe0\xa5K\x16\x0eo\x99\x87\x9d\xd8\xd9c\xbd\x03\xfcMb\x04\x01Z\xd9\xcc\x9e\xdd\xaf3N\xb0\x81\xd554).iwp\x98\xe3\xcb\x04\x93\x97h[\xb2\x84$\xa6\x1dz6K}\xd6\xa2\xb9\x08\x8d\x1d\xc1\x11\xad\xf4aJ\x95\xcb\x14fA\x0c\xb6$\x0b\xd2\x93\xbdc\xaa\x03\xd0\xa9\xad2\x0e\x01H\xb72\x80:\xb0\xf9Y\xf4.\xe4\x8b\xac\xee\xb9\x03]D\x97nq\xe0I\xb4sG\x03\x93\x11\xc5\x90C\x88?L4`Ze\xdeZ\xe4B\t\x02_w\x1c\x80\n\xfdH%G/\xc9+\xb8%\x18\x95\xd9\x12\xdd\x9dv\xf5X@\x84\x81\xb7\xec\x8d\xe3\r\x93\xc5~\xe6\x91\n\xb49\xa5\xd8\xd0\xd0\x1f\xd5\x86"t\x13\xe4g~\x04\xfe\xe0Q\x8d\x04\xd5\xc7M\x08\xc6[\xcd\x0c[\xb31\xe3\xfa\xef\x0f\x03\xc5\x1c@\xb6\xde#\x0b\xd2\xa5\x8fv\xda\xc5\x8d4I\x02FJ\xa52_\x96\xb5\xbd\xb8\x06L\xa8bH\xfc\xfa\x9a\xa3\x0e\xdf!/7\x05\xbd\xe0\xa8\xc3\x01\x9b]\xd44\xce`Nk\x89\x14\x0e\x9am\xe5a\\V+\x10#d\x8f\xc4\x84\x97{E=\xb6\xadqHm\xbd;(\xcc\xc6O\x15[W\xd0\x99x7-\xdd\x92\xe6{\xe8\x1b\r\xc6>\x84ED\xab3d\xac\x8ag\xc2\xd4j\t\xb2\xef\x16\n\xd3\x0e\xbdk\x89\xee\x10#xA\xc5\x10O\xf0\tZC\xc91\x10\xb02\xdc+\x95e\r\xd5\xfb\xde\xe1\x18n\xf5\xe7\x8d\x83FCG\x13~\xcf\xc1\xa0\x80\xea\x93p\\\xb6A\xbe;?o\xbdqp\xcd\x8a\xd0\xeeB\xa2`h\x9b\xb6 %\xfe\xea2\xbf\x97\xd9\x95SZV<\xc8\x91\x9a\xe3\xd2\xafq1Q\xaa?\x85l\xc3h;y\n\xd9\xfc\xc9\xa7\xc8\x83\x1d`82\x81\xa4kl\xab\xd5\x8c\xaamW\x0c\xfeh\xed\xb6\xd8\x97(\r+\x91~\xd0\xc5\x8f)[\xd7V\xce\xc0\x93\xc7\x89\xdc\xeb\xbd\t\x16\xfe\xe0P\x11\xd7<\xbcxylW\x86Tfto\x9b\x9clv\x0fX\xfe9kH!\x82_%AEk\xee\x8b\xd6\xa9\xa4\x9aS\x10\n\xb4'


class PlayerState(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


def create_offline_player(*args, **kwargs):
    return OfflinePlayer.create_offline_player(*args, **kwargs)


def create_online_player(*args, **kwargs):
    return MicrosoftPlayer.create_online_player(*args, **kwargs)


class OnlinePlayer(Player):
    pass


class MicrosoftPlayer(OnlinePlayer):
    @classmethod
    def create_online_player(cls, user_name, user_uuid, access_token, has_mc):
        return cls(user_name, user_uuid, access_token, has_mc)
    
    @property
    def player_accountType(self):
        return ("online", "msa", PlayerState.ONLINE)
    
    def __iter__(self):
        for i in super().__iter__():
            yield i
        yield "msa"


class OfflinePlayer(Player):
    @classmethod
    def create_offline_player(cls, user_name, has_mc, exp=86400):
        user_uuid = str(uuid.uuid4())
        access_token = jwt.encode(
            payload={
                "xuid": str(random.randint(1111111111111111, 9999999999999999)),
                "agg": "Adult",
                "sub": str(uuid.UUID(bytes=random.randbytes(16))),
                "auth": "XBOX",
                "ns": "default",
                "roles": [],
                "iss": "authentication",
                "flags": [
                    "multiplayer"
                ],
                "profiles": {
                    "mc": str(user_uuid)
                },
                "platform": "PC_LAUNCHER",
                "pfd": [
                    {
                        "type": "mc",
                        "id": user_uuid,
                        "name": user_name
                    }
                ],
                "nbf": round(time.time()),
                "exp": round(time.time()) + exp,
                "iat": round(time.time())
            },
            key=secret_key,
            # algorithm="RS256"
        )
        return cls(user_name, user_uuid, access_token, has_mc)
    
    @property
    def player_accountType(self):
        return "offline", "msa", PlayerState.OFFLINE
    
    def __iter__(self):
        for i in super().__iter__():
            yield i
        yield "msa"


class AuthlibInjectorPlayer(OnlinePlayer):
    def __init__(self, user_name: Optional[str], user_uuid: Optional[str], access_token: Optional[str],
                 authlib_injector_path: Optional[Union[str, os.PathLike[str], Path]],
                 signature_publickey: Optional[str], auth_server: Optional[str], has_mc: bool):
        super().__init__(user_name, user_uuid, access_token, has_mc)
        self.__player_authlibInjectorPath = Path(authlib_injector_path)
        self.__player_signaturePublickey = signature_publickey
        self.__player_authServer = auth_server
    
    @property
    def player_authlibInjectorPath(self) -> Optional[Path]:
        return Path(self.__player_authlibInjectorPath)
    
    @player_authlibInjectorPath.setter
    def player_authlibInjectorPath(self, value: Optional[Union[str, os.PathLike[str], Path]]):
        self.__player_authlibInjectorPath = Path(value)
    
    @property
    def player_signaturePublickey(self) -> Optional[str]:
        return self.__player_signaturePublickey
    
    @player_signaturePublickey.setter
    def player_signaturePublickey(self, value: Optional[str]):
        self.__player_signaturePublickey = value
    
    @property
    def player_authServer(self) -> Optional[str]:
        return self.__player_authServer
    
    @player_authServer.setter
    def player_authServer(self, value: Optional[str]):
        self.__player_authServer = value
    
    @property
    def player_accountType(self):
        return "online", "authlib-injector", PlayerState.ONLINE


class LittleSkinPlayer(AuthlibInjectorPlayer):
    @property
    def player_accountType(self):
        return "online", "littleskin", PlayerState.ONLINE
