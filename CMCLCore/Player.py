# -*- coding: utf-8 -*-
from enum import Enum
import uuid
import jwt
import random
import time

secret_key = b"A0I5GLHNA4II2HQ898Q54K34C9RN2PB390R2GCJ09OVK6GP3C4RJOHA89L8NAMIJ8OK4AO3P9H6K4U3OACGMGNHN90K4AS98C5C48DJ4C9RMCIRLA1JNKQ3JACQJIRHKB8KJ0UR4ADRJ48959DO7O9IH9LMJMFRU9LP6QTQFADBNMKJSCHUJSBBRAOVMMO9V9DG7QS21A50K4QQ0CHQ6UDH89P6MO9ABCCO6COPBCDQKCJJEA9D2GAPPB4L4GO988T12QTQG8T0L8A2VA1K6CHH39P6NQA2V8LMM6T9DALQ7SVBQ9PLIGH9U8HM6OSA49PN3QO2CATLKEP2JB9T4AK3KADR7KLIU9CQK4PBK9H944LIN8SLJ0JPUC4SKMTANALA28FR08PLMCAQ89TMMM9JN8TJKOH9MAP8LEVA3CHU4EIRLA155CLPIA1I60E1T89A76CIJCL4I6JPLC4R6SGQ48T2JIGRA9H8I2AI98SKJML9898SMMQ1B9LU3SSBQ8OU38AQ9A8J2QHBM9COJCPQIA1KJIT2ECH87KAA5CLPK6SI0AT6K6EQL8DG6AUQQ9H97C9IN9HR2CHJ09L630OPJA1J32PPPALQ7ELQN89A6G8R09516KLPH9997G9HIA5CM4F3N9HTMUHRHAL7L2RJP9P3MSGI89KVNKE98AT4IAOA29LF62M2C9OMI8KQO9P776LBH911J2QJS9HPM6AQLA4K3ITRK9HA2MKRK9HTNCCQLAT4KIR269H944ARG8SKL2HPSADD6GP3I"


class PlayerState(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class Player:
    def __init__(self, user_name, user_uuid, access_token, has_mc):
        self.__player_name = user_name
        self.__player_uuid = user_uuid
        self.__player_accessToken = access_token
        self.__player_hasMC = has_mc
    
    def __iter__(self):
        yield self.__player_name
        yield self.__player_uuid
        yield self.__player_accessToken
        yield self.__player_accountType[1]
        yield self.__player_hasMC
    
    def __bool__(self):
        return bool(self.__player_name and self.__player_uuid and self.__player_accessToken)
    
    def __getitem__(self, item):
        return eval(f"self.__player_{item}")
    
    def __setitem__(self, key, value):
        exec(f"self.__player_{key} = {value}")
    
    def __cmp__(self, other):
        if isinstance(other, Player):
            return self.player_name == other.player_name and self.player_uuid == other.player_uuid and self.player_accessToken == other.player_accessToken and self.player_hasMC == other.player_hasMC and self.player_accountType == other.player_accountType
        else:
            raise TypeError(f"cannot compare with type `{type(other)}`")
    
    @property
    def player_name(self):
        return self.__player_name
    
    @player_name.setter
    def player_name(self, value):
        self.__player_name = value
    
    @property
    def player_uuid(self):
        return self.__player_uuid
    
    @player_uuid.setter
    def player_uuid(self, value):
        self.__player_uuid = value
    
    @property
    def player_accessToken(self):
        return self.__player_accessToken
    
    @player_accessToken.setter
    def player_accessToken(self, value):
        self.__player_accessToken = value
    
    @property
    def player_hasMC(self):
        return self.__player_hasMC
    
    @player_hasMC.setter
    def player_hasMC(self, value):
        self.__player_hasMC = value
    
    @classmethod
    def create_offline_player(cls, *args, **kwargs):
        return OfflinePlayer.create_offline_player(*args, **kwargs)
    
    @classmethod
    def create_online_player(cls, *args, **kwargs):
        return MicrosoftPlayer.create_online_player(*args, **kwargs)


class OnlinePlayer(Player):
    pass


class MicrosoftPlayer(OnlinePlayer):
    @classmethod
    def create_online_player(cls, user_name, user_uuid, access_token, has_mc, is_empty=False):
        return cls(user_name, user_uuid, access_token, has_mc)
    
    @property
    def player_accountType(self):
        return ("online", "msa", PlayerState.ONLINE)


class OfflinePlayer(Player):
    @classmethod
    def create_offline_player(cls, user_name, has_mc):
        user_uuid = str(uuid.uuid4()).replace("-", "")
        access_token = jwt.encode(
            {
                "xuid": str(random.randint(1111111111111111, 9999999999999999)),
                "agg": "Adult",
                "sub": str(uuid.UUID(bytes=random.randbytes(16))),
                "auth": "XBOX",
                "ns": "default",
                "roles": [],
                "iss": "authentication",
                "flags": ["multiplayer"],
                "profiles": {
                    "mc": str(uuid.UUID(user_uuid))
                },
                "platform": "UNKNOWN",
                "yuid": str(uuid.UUID(bytes=random.randbytes(16))).replace("-", ""),
                "nbf": round(time.time()),
                "exp": round(time.time()) + 86400,
                "iat": round(time.time())
            },
            key=secret_key
        )
        return cls(user_name, user_uuid, access_token, has_mc)
    
    @property
    def player_accountType(self):
        return ("offline", "msa", PlayerState.OFFLINE)
