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

secret_key = b'\xf9\xad\x16\xa5\x85\xa7`t\x95\xb6\x9bP(U\xd8\x92\x00:\xaeI\xa5\xeeO\xe9\xf8\xb8\xbc\x1d\xb8\xa3\x18\xf6\xc8`\x9e\xef[I\x19\xb9\xd0\x83~l#\x7f\x8do\x12\xf8w\xf8\x9d\x08\x8dH%\x13A\x83\xc8bz\xe6\xaf\x87\x82\xf4\x83\xca[\x957\x9f\xa1>=\xaa\x13n\x04_\xd54>\x8c\x8e\xa6\xa2\x0e\xa8\xe0\x83\x8ekz\x90\xcd\xfa\xdb#\xad#\xe8\x01\xa1=jr\x1e\xca\x0f\xcb6\x8e\xdb\xa8J\x06\x9e\xca_i]\xd9hz1\x83_\xfa/ \\!jOz[\x939\x01t\x9fT @\x95\xe1\x1d\xb0\x90\x05\xa2q\xb7V\x91f\xaa=\x87\xed\xc5@\x85Hh\xf7\xdfP,\xd6:\xa1a\x0e\xc4K\xfd7O\xd0>\xf1\xdf\x99\x9b\xd5\x87a\x81\xc9\xf6h\x12\xf1\xd9V\xa3\xe5u\xa8V\xd5\x80y\xfd\x88.hJ\xd9\xcd3q\x08\xc8\xdc\x11\xf5\xed\x84\xf3\x9e\xe0\xaf\x84\xa7\x16\xaah\n\xff\xce\xf7\xfb\xc2Wyu\x86\xe2\xa9\xc0&IF\xcd_\x83\xd7\xb8\xe4\xfaf\xdc\xa1\xf6\x8c\rJT\xef\xbex\xb3*W\x7fZ%:C\x97\x8e\x7f\x1e.\xec\xd0\x86\x13Ld\x89\xed\xf0h\xf6g\x8e\xe2\xfeu\x98s\xc7Q\xa8\xb0\'\xa5jS\x86.S.Y\x1ci\x1d\x0eq\x9f\x90=\x98\n\x85\x8de5D\x99\xaa\xfb\x94\xbeY\xaam4|#\x19@\x93W;v\x8d\xd2@\xc9\xaf\x1ac\x89\x80\xfa\x0e\xcb]\xdb\x10\xcd\xaa\x15)\x14qi\xf0\xc4t\x9cp\x07\x9d\xa7\xf7\xbf\\\x92(o\xd7\xbb\x83Y\x80*T\xd1G\xd6\xfepRNa4\x02\xb7\xc7\xbd\x15\xbf\xf7\xf9-,\x9f_\xado,\xb2#:\xfeN\x0e`%v>\t\x9b\xe7\xfcT\xe36\xec\xc0&\x103\xfbRb\x97\x11\xacZAQ \xb5\x8c\xd4\xe66P\xac\xb0\xd1\xadQ\x87\xe5\xbb>\x92FU\xe93\xd2\x9d2\xd1\x17K\x9c\x82vl@\x8a\xdc\xa8\x1a\xf7\xbb\x08\x88\x955\xc8\x11T\xdf\xd7{\xf61\xe4w.L*\x9a[\xfb\\\xe9\xd2\x073\xc8VR\xf6\x0er\xe0\xc7\xca\x07J\xd4\xed\xabkW\x9ef42\x90\x8e\xc8\xbc\xb5MX\xab)XWn\xcf\x8d\x02O\xa9l\x86}\x8a\x8d\xfc\x1b\xe1f\xfd\x0f+\xf7\xf6\x1cL\x99_\xace\x90F\xc8j\x06%\x89\no\x06\xc4io_\xcaYH\x15\xac\x01\xc1\x9f\xeb\xc2\xf6x?_rz\xc2\xfdy\xd7\x08\x8a\xff\x19\x0b\xa0<\xa6\xc2\x9f\xaa\xf9\xe6\xea\xecH(\xed\xd2Dl6\x91\x03\t<\x84\n\xac\xee\xe2a\xaf\xef%d\x02Ti\x80\xb3\x18\xf5\xe9\x89"Ao%\xfd\x13Ht\xcb\n\x14\x99Kz/^{9tI\xce\xe6\xdc\x9d=\xe6\x92\x0b$\xf6\x0c\xd9\xb3\xe7\xff Ek\xb2\xfb\xa1\x1c\xb3\xa8\xf3\xf6\xa7@vk\x83x\xd2\x8a\x8c|\x81\x01a\xb9\xd25\xce4\x9c\xea\x07#~\xbf,$\xf6\xbb&@\xc5\x10\x1e4-\xcc\x94\xb2[\xd4\xbc\xdb\x92\xd3\xae%\xb6\x14\xf5W\x16h\xfd`;\xf6\xf3R\xb4\x0f\x9fKU<\x80\x8f\n\xdf\xf9!\x88Jb\xa5\xf0\xba\xedKnT\xe6\xc3\x92UrO7\x04\xd1B52\xf3>^:\xd1u\xcd'


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
