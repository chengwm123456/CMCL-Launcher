# -*- coding: utf-8 -*-
import os
from typing import *

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..GetOperationSystem import GetOperationSystemInMojangApi


@dataclass(slots=True)
class Minecraft:
    mc_gameVersion: Union[str, LiteralString] = field(default="")
    mc_gamePlatform: str = field(default_factory=GetOperationSystemInMojangApi)
    mc_gameWorkDir: Union[str, os.PathLike[str], Path] = ""
    mc_gameJarFile: Union[str, os.PathLike[str], Path] = ""
    mc_gameJsonFile: Union[str, os.PathLike[str], Path] = ""
    mc_gameNativesDir: Union[str, os.PathLike[str], Path] = ""
    mc_gameAssetsDir: Union[str, os.PathLike[str], Path] = ""
    mc_gameLibrariesDir: Union[str, os.PathLike[str], Path] = ""
    
    def __post_init__(self):
        self.mc_gameVersion = str(self.mc_gameVersion)
        self.mc_gamePlatform = str(self.mc_gamePlatform)
        self.mc_gameWorkDir = Path(self.mc_gameWorkDir).absolute()
        self.mc_gameJarFile = Path(self.mc_gameJarFile).absolute()
        self.mc_gameJsonFile = Path(self.mc_gameJsonFile).absolute()
        self.mc_gameNativesDir = Path(self.mc_gameNativesDir).absolute()
        self.mc_gameAssetsDir = Path(self.mc_gameAssetsDir).absolute()
        self.mc_gameLibrariesDir = Path(self.mc_gameLibrariesDir).absolute()
    
    @property
    def mc_gameJsonFileContent(self) -> Dict[Any, Any]:
        if self.mc_gameJsonFile and Path(self.mc_gameJsonFile).exists():
            try:
                return json.loads(Path(self.mc_gameJsonFile).read_text(encoding="utf-8"))
            except:
                return {}
        return {}
    
    @property
    def mc_gameMainClass(self) -> Optional[str]:
        return self.mc_gameJsonFileContent.get("mainClass")
    
    @property
    def mc_gameAssetsIndex(self) -> Optional[str]:
        return self.mc_gameJsonFileContent.get("assets")
    
    @property
    def mc_gameLibrariesFiles(self) -> Iterable[Any]:
        return self.mc_gameJsonFileContent.get("libraries", [])
