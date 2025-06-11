# -*- coding: utf-8 -*-
from typing import *

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class Player:
    player_playerName: Optional[str]
    player_playerUUID: Optional[Union[str, UUID]]
    player_accessToken: Optional[str]
    player_hasMC: bool
    
    def __post_init__(self):
        if self.player_playerName:
            self.player_playerName = str(self.player_playerName)
        if self.player_playerUUID:
            try:
                self.player_playerUUID = str(UUID(str(self.player_playerUUID)))
            except ValueError:
                self.player_playerUUID = str(self.player_playerUUID)
        if self.player_accessToken:
            self.player_accessToken = str(self.player_accessToken)
        if self.player_hasMC:
            self.player_hasMC = bool(self.player_hasMC)
    
    def __bool__(self):
        return self.player_playerName and self.player_playerUUID and self.player_accessToken
