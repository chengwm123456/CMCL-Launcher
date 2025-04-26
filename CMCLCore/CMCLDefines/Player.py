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
        self.__player_uuid = UUID(user_uuid) if user_uuid else None
        self.__player_accessToken = access_token
        self.__player_hasMC = has_mc
    
    def __iter__(self) -> Iterable[Union[Optional[str], bool, UUID]]:
        yield self.__player_name
        yield str(UUID(str(self.__player_uuid))) if self.__player_uuid else None
        yield self.__player_accessToken
        yield self.__player_hasMC
    
    def __bool__(self) -> bool:
        return bool(self.__player_name and (
            str(UUID(str(self.__player_uuid))) if self.__player_uuid else None) and self.__player_accessToken)
    
    def __getitem__(self, item: str) -> Optional[Any]:
        try:
            return eval(f"self.__player_{item}", globals(), locals())
        finally:
            pass
    
    def __setitem__(self, key: str, value: Any):
        exec(f"self.__player_{key} = \"{value}\"", globals(), locals())
    
    def __cmp__(self, other: Any) -> bool:
        if isinstance(other, Player):
            return self.player_name == other.player_name and self.player_uuid == other.player_uuid and self.player_accessToken == other.player_accessToken and self.player_hasMC == other.player_hasMC
        else:
            return False
    
    @property
    def player_name(self) -> Optional[str]:
        return self.__player_name
    
    @player_name.setter
    def player_name(self, value: Optional[str]):
        self.__player_name = value
    
    @property
    def player_uuid(self) -> Optional[str]:
        return str(UUID(str(self.__player_uuid))) if self.__player_uuid else None
    
    @player_uuid.setter
    def player_uuid(self, value: Optional[Union[str, UUID]]):
        self.__player_uuid = str(UUID(str(value))) if value else None
    
    @property
    def player_accessToken(self) -> Optional[str]:
        return self.__player_accessToken
    
    @player_accessToken.setter
    def player_accessToken(self, value: Optional[str]):
        self.__player_accessToken = value
    
    @property
    def player_hasMC(self) -> bool:
        return self.__player_hasMC
    
    @player_hasMC.setter
    def player_hasMC(self, value: bool):
        self.__player_hasMC = value
