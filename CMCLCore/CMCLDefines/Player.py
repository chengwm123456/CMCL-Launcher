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
        self.__player_name = user_name
        try:
            self.__player_uuid = str(UUID(str(user_uuid))) or user_uuid
        except ValueError:
            self.__player_uuid = user_uuid
        self.__player_accessToken = access_token
        self.__player_hasMC = has_mc
    
    def __iter__(self) -> Iterable[Union[Optional[str], bool]]:
        for item in self.__player_name, self.__player_uuid, self.__player_accessToken, self.__player_hasMC:
            yield item
    
    def __bool__(self) -> bool:
        return bool(self.__player_name and self.__player_uuid and self.__player_accessToken)
    
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
    def player_name(self) -> Optional[str]:
        return self.__player_name
    
    @player_name.setter
    def player_name(self, value: Optional[str]):
        self.__player_name = value
    
    @property
    def player_uuid(self) -> Optional[str]:
        try:
            return str(UUID(str(self.__player_uuid)))
        except ValueError:
            return str(self.__player_uuid)
    
    @player_uuid.setter
    def player_uuid(self, value: Optional[Union[str, UUID]]):
        try:
            self.__player_uuid = str(UUID(str(value))) or value
        except ValueError:
            self.__player_uuid = value
    
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
