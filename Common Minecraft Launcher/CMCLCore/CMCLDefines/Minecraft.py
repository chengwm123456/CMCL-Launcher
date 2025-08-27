# -*- coding: utf-8 -*-
import os
from typing import *

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..GetOperationSystem import GetOperationSystemInMojangAPI


@dataclass(slots=True, unsafe_hash=True)
class Minecraft:
    mc_gameVersion: Union[str, LiteralString] = field(default="")
    mc_inheritsFrom: Optional[str] = None
    mc_gamePlatformName: Union[str, LiteralString] = field(
        default_factory=lambda: GetOperationSystemInMojangAPI()[0])
    mc_gamePlatformMachine: Union[str, LiteralString] = field(
        default_factory=lambda: GetOperationSystemInMojangAPI()[1])
    mc_gameWorkDir: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gamePlayDir: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gameJarFile: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gameJsonFile: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gameNativesDir: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gameAssetsDir: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gameLibrariesDir: Union[str, os.PathLike[str], Path, LiteralString] = ""
    mc_gameSeparation: bool = False
    
    def __post_init__(self):
        self.mc_gameVersion = str(self.mc_gameVersion)
        self.mc_gamePlatformName = str(self.mc_gamePlatformName)
        self.mc_gamePlatformMachine = str(self.mc_gamePlatformMachine)
        self.mc_gameWorkDir = Path(self.mc_gameWorkDir).absolute()
        self.mc_gamePlayDir = self.mc_gameWorkDir
        self.mc_gameJarFile = Path(self.mc_gameJarFile).absolute()
        self.mc_gameJsonFile = Path(self.mc_gameJsonFile).absolute()
        self.mc_gameNativesDir = Path(self.mc_gameNativesDir).absolute()
        self.mc_gameAssetsDir = Path(self.mc_gameAssetsDir).absolute()
        self.mc_gameLibrariesDir = Path(self.mc_gameLibrariesDir).absolute()
        self.mc_gameSeparation = bool(self.mc_gameSeparation)
        if self.mc_gameSeparation:
            self.mc_gamePlayDir = self.mc_gameWorkDir / "versions" / self.mc_gameVersion
        
        jsonFile = self.mc_gameJsonFileContent
        if jsonFile:
            self.mc_inheritsFrom = jsonFile.get("inheritsFrom")
            if self.mc_inheritsFrom:
                self.mc_gameJarFile = self.mc_gameJarFile.parent.parent / self.mc_inheritsFrom / f"{self.mc_inheritsFrom}.jar"
    
    def __bool__(self) -> bool:
        return bool(
            ((self.mc_gameVersion and self.mc_inheritsFrom)
             and self.mc_gamePlatformName and self.mc_gamePlatformMachine
             and self.mc_gameWorkDir and self.mc_gamePlayDir
             and self.mc_gameJarFile and self.mc_gameJsonFile
             and self.mc_gameNativesDir and self.mc_gameAssetsDir and self.mc_gameLibrariesDir)
        )
    
    @property
    def mc_gameJsonFileContent(self) -> Dict[Any, Any]:
        if self.mc_gameJsonFile and Path(self.mc_gameJsonFile).exists():
            try:
                jsonFileContent = json.loads(Path(self.mc_gameJsonFile).read_text(encoding="utf-8"))
                if self.mc_inheritsFrom:
                    inheritsJsonFile = json.loads(Path(
                        self.mc_gameJsonFile.parent.parent / self.mc_inheritsFrom / f"{self.mc_inheritsFrom}.json"
                    ).read_text(encoding="utf-8"))
                    if inheritsJsonFile.get("arguments"):
                        jsonFileContent["arguments"]["game"] = (inheritsJsonFile["arguments"]["game"]
                                                                + jsonFileContent["arguments"]["game"])
                        jsonFileContent["arguments"]["jvm"] = (inheritsJsonFile["arguments"]["jvm"]
                                                               + jsonFileContent["arguments"]["jvm"])
                    elif inheritsJsonFile.get("minecraftArguments"):
                        jsonFileContent["minecraftArguments"] = inheritsJsonFile["minecraftArguments"]
                    if inheritsJsonFile.get("libraries"):
                        jsonFileContent["libraries"] = inheritsJsonFile["libraries"] + jsonFileContent["libraries"]
                    if inheritsJsonFile.get("assets"):
                        jsonFileContent["assets"] = inheritsJsonFile["assets"]
                    if inheritsJsonFile.get("assetIndex"):
                        jsonFileContent["assetIndex"] = inheritsJsonFile["assetIndex"]
                    
                    if inheritsJsonFile.get("javaVersion"):
                        jsonFileContent["javaVersion"] = inheritsJsonFile["javaVersion"]
                return jsonFileContent
            except:
                return {}
        return {}
