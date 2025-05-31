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
    
    def __post_init__(self):
        if self.mc_gameVersion:
            self.mc_gameVersion = str(self.mc_gameVersion)
        if self.mc_gameWorkDir:
            self.mc_gameWorkDir = Path(self.mc_gameWorkDir).absolute()
        if self.mc_gameJarFile:
            self.mc_gameJarFile = Path(self.mc_gameJarFile).with_suffix(".jar").absolute()
        if self.mc_gameJsonFile:
            self.mc_gameJsonFile = Path(self.mc_gameJsonFile).with_suffix(".json").absolute()
        if self.mc_gameNativesDir:
            self.mc_gameNativesDir = Path(self.mc_gameNativesDir).absolute()
        if self.mc_gameAssetsDir:
            self.mc_gameAssetsDir = Path(self.mc_gameAssetsDir).absolute()
        if self.mc_gameLibrariesDir:
            self.mc_gameLibrariesDir = Path(self.mc_gameLibrariesDir).absolute()
    
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
