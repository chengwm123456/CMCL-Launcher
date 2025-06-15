# -*- coding: utf-8 -*-
import os
import uuid
import jwt
import random
import time
from pathlib import Path
from .CMCLDefines.Player import Player
from typing import *
from enum import Enum

secret_key = b"A0I5GLHNA4II2HQ898Q54K34C9RN2PB390R2GCJ09OVK6GP3C4RJOHA89L8NAMIJ8OK4AO3P9H6K4U3OACGMGNHN90K4AS98C5C48DJ4C9RMCIRLA1JNKQ3JACQJIRHKB8KJ0UR4ADRJ48959DO7O9IH9LMJMFRU9LP6QTQFADBNMKJSCHUJSBBRAOVMMO9V9DG7QS21A50K4QQ0CHQ6UDH89P6MO9ABCCO6COPBCDQKCJJEA9D2GAPPB4L4GO988T12QTQG8T0L8A2VA1K6CHH39P6NQA2V8LMM6T9DALQ7SVBQ9PLIGH9U8HM6OSA49PN3QO2CATLKEP2JB9T4AK3KADR7KLIU9CQK4PBK9H944LIN8SLJ0JPUC4SKMTANALA28FR08PLMCAQ89TMMM9JN8TJKOH9MAP8LEVA3CHU4EIRLA155CLPIA1I60E1T89A76CIJCL4I6JPLC4R6SGQ48T2JIGRA9H8I2AI98SKJML9898SMMQ1B9LU3SSBQ8OU38AQ9A8J2QHBM9COJCPQIA1KJIT2ECH87KAA5CLPK6SI0AT6K6EQL8DG6AUQQ9H97C9IN9HR2CHJ09L630OPJA1J32PPPALQ7ELQN89A6G8R09516KLPH9997G9HIA5CM4F3N9HTMUHRHAL7L2RJP9P3MSGI89KVNKE98AT4IAOA29LF62M2C9OMI8KQO9P776LBH911J2QJS9HPM6AQLA4K3ITRK9HA2MKRK9HTNCCQLAT4KIR269H944ARG8SKL2HPSADD6GP3I"


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
    def create_offline_player(cls, user_name, has_mc):
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
                "exp": round(time.time()) + 86400,
                "iat": round(time.time())
            },
            key=secret_key,
            algorithm="RS256"
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
