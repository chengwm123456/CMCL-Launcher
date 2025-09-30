# -*- coding: utf-8 -*-
from typing import *

from dataclasses import dataclass
from uuid import UUID


class Player:
    __slots__ = ("__player_playerName", "__player_playerUUID", "__player_accessToken", "__player_hasMC",
                 "__player_profileJSON")
    
    def __init__(
            self,
            player_playerName: Optional[str],
            player_playerUUID: Optional[Union[str, UUID]],
            player_accessToken: Optional[str],
            player_hasMC: bool,
            player_profileJSON: Mapping[Any, Any] = {}
    ):
        self.__player_playerName = player_playerName
        if isinstance(player_playerUUID, str):
            try:
                self.__player_playerUUID = str(UUID(player_playerUUID))
            except ValueError:
                self.__player_playerUUID = None
        else:
            self.__player_playerUUID = str(player_playerUUID)
        self.__player_accessToken = player_accessToken
        self.__player_hasMC = player_hasMC
        self.__player_profileJSON = player_profileJSON
    
    @property
    def player_playerName(self) -> Optional[str]:
        return str(self.__player_playerName) if self.__player_playerName is not None else None
    
    @player_playerName.setter
    def player_playerName(self, value: Optional[str]):
        if value is not None:
            self.__player_playerName = str(value)
        else:
            self.__player_playerName = value
    
    @property
    def player_playerUUID(self) -> Optional[str]:
        return str(self.__player_playerUUID) if self.__player_playerUUID is not None else None
    
    @player_playerUUID.setter
    def player_playerUUID(self, value: Optional[Union[str, UUID]]):
        if value is not None:
            if isinstance(value, str):
                try:
                    self.__player_playerUUID = str(UUID(value))
                except:
                    self.__player_playerUUID = None
            else:
                self.__player_playerUUID = str(value)
        else:
            self.__player_playerUUID = value
    
    @property
    def player_accessToken(self) -> Optional[str]:
        return str(self.__player_accessToken) if self.__player_accessToken is not None else None
    
    @player_accessToken.setter
    def player_accessToken(self, value: Optional[str]):
        if value is not None:
            self.__player_accessToken = str(value)
        else:
            self.__player_accessToken = value
    
    @property
    def player_hasMC(self) -> bool:
        return bool(self.__player_hasMC)
    
    @player_hasMC.setter
    def player_hasMC(self, value: Optional[bool]):
        self.__player_hasMC = bool(value)
    
    def __bool__(self) -> bool:
        return bool(self.player_playerName and self.player_playerUUID and self.player_accessToken)
