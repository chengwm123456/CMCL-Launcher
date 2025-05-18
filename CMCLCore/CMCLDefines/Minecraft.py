# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
from typing import *
import os
import json


@dataclass
class Minecraft:
    mc_gameVersion: Optional[str]
    mc_gameWorkDir: Optional[Union[str, os.PathLike[str]]]
    mc_gameJarFile: Optional[Union[str, os.PathLike[str]]]
    mc_gameJsonFile: Optional[Union[str, os.PathLike[str]]]
    mc_gameNativesDir: Optional[Union[str, os.PathLike[str]]]
    mc_gameAssetsDir: Optional[Union[str, os.PathLike[str]]]
    mc_gameLibrariesDir: Optional[Union[str, os.PathLike[str]]]
    
    @property
    def mc_gameJsonFileContent(self) -> Optional[dict]:
        if self.mc_gameJsonFile and Path(self.mc_gameJsonFile).exists():
            try:
                return json.loads(Path(self.mc_gameJsonFile).read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return None
    
    @property
    def mc_gameMainClass(self) -> Optional[str]:
        return (self.mc_gameJsonFileContent or {}).get("mainClass")
    
    @property
    def mc_gameAssetsIndex(self) -> Optional[str]:
        return (self.mc_gameJsonFileContent or {}).get("assets")
    
    @property
    def mc_gameLibrariesFiles(self) -> Iterable[Any]:
        return (self.mc_gameJsonFileContent or {}).get("libraries", [])
