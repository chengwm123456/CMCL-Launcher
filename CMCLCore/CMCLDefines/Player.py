# -*- coding: utf-8 -*-
from typing import *
from uuid import UUID


class Player:
    def __init__(
            self,
            user_name: Optional[str],
            user_uuid: Optional[Union[str, UUID]],
            access_token: Optional[str],
            has_mc: bool
    ):
        self.__player_playerName = user_name
        try:
            self.__player_playerUUID = str(UUID(str(user_uuid))) or user_uuid
        except ValueError:
            self.__player_playerUUID = user_uuid
        self.__player_accessToken = access_token
        self.__player_hasMC = has_mc
    
    def __iter__(self) -> Iterable[Union[Optional[str], bool]]:
        for item in (self.__player_playerName, self.__player_playerUUID,
                     self.__player_accessToken, self.__player_hasMC):
            yield item
    
    def __bool__(self) -> bool:
        return any(self.__iter__()[:-1])
    
    def __getitem__(self, item: str) -> Optional[Any]:
        try:
            return eval(f"self.__player_{item}", globals(), locals())
        finally:
            pass
    
    def __setitem__(self, key: str, value: Any):
        exec(f"self.__player_{key} = \"{value}\"", globals(), locals())
    
    def __cmp__(self, other: Any) -> bool:
        if isinstance(other, Player):
            return tuple(self.__iter__()) == tuple(other.__iter__())
        else:
            return super().__cmp__(other)
    
    @property
    def player_playerName(self) -> Optional[str]:
        return self.__player_playerName
    
    @player_playerName.setter
    def player_playerName(self, value: Optional[str]):
        self.__player_playerName = value
    
    @property
    def player_playerUUID(self) -> Optional[str]:
        try:
            return str(UUID(str(self.__player_playerUUID)))
        except ValueError:
            return str(self.__player_playerUUID)
    
    @player_playerUUID.setter
    def player_playerUUID(self, value: Optional[Union[str, UUID]]):
        try:
            self.__player_playerUUID = str(UUID(str(value))) or value
        except ValueError:
            self.__player_playerUUID = value
    
    @property
    def player_accessToken(self) -> Optional[str]:
        return self.__player_accessToken
    
    @player_accessToken.setter
    def player_accessToken(self, value: Optional[str]):
        self.__player_accessToken = value
    
    @property
    def player_hasMC(self) -> bool:
        return bool(self.__player_hasMC)
    
    @player_hasMC.setter
    def player_hasMC(self, value: bool):
        self.__player_hasMC = bool(value)
