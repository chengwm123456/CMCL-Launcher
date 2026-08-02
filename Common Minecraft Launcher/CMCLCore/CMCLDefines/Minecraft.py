# -*- coding: utf-8 -*-
import os
from typing import *

import json
from pathlib import Path

from ..GetOperationSystem import GetOperationSystemInMojangAPI
from ..CMCLCache.CacheManager import CacheManager


class Minecraft:
    __slots__ = (
        "__mc_gameVersion",
        "__mc_gameWorkDir", "__mc_gamePlayDir",
        "__mc_gameJarFile", "__mc_gameJsonFile",
        "__mc_gameNativesDir", "__mc_gameAssetsDir", "__mc_gameLibrariesDir",
        "__mc_gameSeparation",
        
        "cacheManager"
    )
    
    def __init__(
            self,
            mc_gameVersion: Union[str, LiteralString] = "",
            mc_gameWorkDir: Union[str, os.PathLike[str], LiteralString] = "",
            mc_gameJarFile: Union[str, os.PathLike[str], LiteralString] = "",
            mc_gameJsonFile: Union[str, os.PathLike[str], LiteralString] = "",
            mc_gameNativesDir: Union[str, os.PathLike[str], LiteralString] = "",
            mc_gameAssetsDir: Union[str, os.PathLike[str], LiteralString] = "",
            mc_gameLibrariesDir: Union[str, os.PathLike[str], LiteralString] = "",
            mc_gameSeparation: bool = False
    ):
        self.__mc_gameVersion = str(mc_gameVersion)
        self.__mc_gameWorkDir = Path(mc_gameWorkDir).resolve()
        self.__mc_gamePlayDir = Path(mc_gameWorkDir).resolve()
        self.__mc_gameJarFile = Path(mc_gameJarFile).resolve()
        self.__mc_gameJsonFile = Path(mc_gameJsonFile).resolve()
        self.__mc_gameNativesDir = Path(mc_gameNativesDir).resolve()
        self.__mc_gameAssetsDir = Path(mc_gameAssetsDir).resolve()
        self.__mc_gameLibrariesDir = Path(mc_gameLibrariesDir).resolve()
        self.__mc_gameSeparation = bool(mc_gameSeparation)
        if self.__mc_gameSeparation:
            self.__mc_gamePlayDir = self.__mc_gameWorkDir / "versions" / self.__mc_gameVersion
        
        self.cacheManager = CacheManager()
    
    def __bool__(self) -> bool:
        return bool(
            (((self.mc_gameVersion and self.mc_inheritsFrom) or self.mc_gameVersion)
             and self.mc_gamePlatformName and self.mc_gamePlatformMachine
             and self.mc_gameWorkDir and self.mc_gamePlayDir
             and self.mc_gameJarFile and self.mc_gameJsonFile
             and self.mc_gameNativesDir and self.mc_gameAssetsDir and self.mc_gameLibrariesDir)
        )
    
    def __str__(self) -> str:
        return f"Minecraft(version={self.version}, inheritsFrom={self.inheritsFrom})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def mc_gameVersion(self) -> str:
        return str(self.__mc_gameVersion)
    
    @mc_gameVersion.setter
    def mc_gameVersion(self, value: Union[str, LiteralString]):
        self.__mc_gameVersion = value
    
    @property
    def mc_inheritsFrom(self) -> Optional[str]:
        return json.loads(Path(self.mc_gameJsonFile).read_text(encoding="utf-8")).get("inheritsFrom")
    
    @property
    def mc_gamePlatformName(self) -> str:
        return GetOperationSystemInMojangAPI()[0]
    
    @property
    def mc_gamePlatformMachine(self) -> str:
        return GetOperationSystemInMojangAPI()[1]
    
    @property
    def mc_gameWorkDir(self) -> Path:
        return Path(self.__mc_gameWorkDir)
    
    @mc_gameWorkDir.setter
    def mc_gameWorkDir(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gameWorkDir = Path(value).resolve()
    
    @property
    def mc_gamePlayDir(self) -> Path:
        return Path(self.__mc_gamePlayDir)
    
    @mc_gamePlayDir.setter
    def mc_gamePlayDir(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gamePlayDir = Path(value).resolve()
    
    @property
    def mc_gameJarFile(self) -> Path:
        return Path(self.__mc_gameJarFile)
    
    @mc_gameJarFile.setter
    def mc_gameJarFile(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gameJarFile = Path(value).resolve()
    
    @property
    def mc_gameJsonFile(self) -> Path:
        return Path(self.__mc_gameJsonFile)
    
    @mc_gameJsonFile.setter
    def mc_gameJsonFile(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gameJsonFile = Path(value).resolve()
        self.cacheManager.clearCache()
    
    @property
    def mc_gameNativesDir(self) -> Path:
        return Path(self.__mc_gameNativesDir)
    
    @mc_gameNativesDir.setter
    def mc_gameNativesDir(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gameNativesDir = Path(value).resolve()
    
    @property
    def mc_gameAssetsDir(self) -> Path:
        return Path(self.__mc_gameAssetsDir)
    
    @mc_gameAssetsDir.setter
    def mc_gameAssetsDir(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gameAssetsDir = Path(value).resolve()
    
    @property
    def mc_gameLibrariesDir(self) -> Path:
        return Path(self.__mc_gameLibrariesDir)
    
    @mc_gameLibrariesDir.setter
    def mc_gameLibrariesDir(self, value: Union[str, os.PathLike[str], Path, LiteralString]):
        self.__mc_gameLibrariesDir = Path(value).resolve()
    
    @property
    def mc_gameSeparation(self) -> bool:
        return bool(self.__mc_gameSeparation)
    
    @mc_gameSeparation.setter
    def mc_gameSeparation(self, value: bool):
        self.__mc_gameSeparation = bool(value)
        if self.__mc_gameSeparation:
            self.__mc_gamePlayDir = self.__mc_gameWorkDir / "versions" / self.__mc_gameVersion
    
    @property
    def mc_gameJsonFileContent(self) -> Dict[Any, Any]:
        if self.mc_gameJsonFile and Path(self.mc_gameJsonFile).exists():
            try:
                if self.cacheManager.getCache("jsonFileContent"):
                    jsonFileContent = self.cacheManager.getCache("jsonFileContent")
                else:
                    jsonFileContent = json.loads(Path(self.mc_gameJsonFile).read_text(encoding="utf-8"))
                    self.cacheManager.setCache("jsonFileContent", jsonFileContent, 180)
                if self.mc_inheritsFrom:
                    inheritsJsonFile = json.loads(Path(
                        self.mc_gameJsonFile.parent.parent / self.mc_inheritsFrom / f"{self.mc_inheritsFrom}.json"
                    ).read_text(encoding="utf-8"))
                    # jsonFileContent.update(inheritsJsonFile)
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
