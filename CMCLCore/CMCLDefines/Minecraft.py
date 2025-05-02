# -*- coding: utf-8 -*-
from pathlib import Path, PurePath
from typing import *
import os
import json


class Minecraft:
    def __init__(
            self,
            game_version: str = "",
            game_work_dir: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
            game_jar: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
            game_json: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
            game_natives_dir: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
            game_asset_dir: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
            game_libs: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
    ):
        self.__mc_gameVersion = None
        self.__mc_gameWorkDir = None
        self.__mc_gameJarFile = None
        self.__mc_gameJsonFile = None
        self.__mc_gameJsonFileInfo = None
        self.__mc_gameNativesDir = None
        self.__mc_gameAssetsDir = None
        self.__mc_gameAssetsIndex = None
        self.__mc_gameLibrariesDir = None
        if game_version:
            self.__mc_gameVersion = game_version
        if Path(game_work_dir).is_dir():
            self.__mc_gameWorkDir = Path(game_work_dir).absolute()
        if Path(game_jar).is_file() and Path(game_jar).suffix == ".jar":
            self.__mc_gameJarFile = Path(game_jar).absolute()
        if Path(game_json).is_file() and Path(game_json).suffix == ".json":
            self.__mc_gameJsonFile = Path(game_json).absolute()
            self.__mc_gameJsonFileInfo = json.loads(Path(self.__mc_gameJsonFile).read_text(encoding="utf-8"))
        if Path(game_natives_dir).is_dir():
            self.__mc_gameNativesDir = Path(game_natives_dir).absolute()
        if Path(game_asset_dir).is_dir():
            self.__mc_gameAssetsDir = Path(game_asset_dir).absolute()
            if self.__mc_gameJsonFileInfo:
                self.__mc_gameAssetsIndex = self.__mc_gameJsonFileInfo.get("assets")
        if Path(game_libs).is_dir():
            self.__mc_gameLibrariesDir = Path(game_libs).absolute()
    
    def __iter__(self) -> Iterable[Any]:
        yield self.__mc_gameVersion
        yield self.__mc_gameWorkDir
        yield self.__mc_gameJarFile
        yield self.__mc_gameJsonFile
        yield self.__mc_gameNativesDir
        yield self.__mc_gameAssetsDir
        yield self.__mc_gameLibrariesDir
    
    def __bool__(self) -> bool:
        return bool(
            self.__mc_gameVersion and self.__mc_gameWorkDir and self.__mc_gameJarFile and self.__mc_gameJsonFile and self.__mc_gameNativesDir and self.__mc_gameAssetsDir and self.__mc_gameLibrariesDir)
    
    def __getitem__(self, item: str) -> Optional[Any]:
        try:
            return eval(f"self.__mc_{item}", globals(), locals())
        finally:
            pass
    
    def __setitem__(self, key: str, value: Any):
        exec(f"self.__mc_{key} = {value}", globals(), locals())
    
    def __cmp__(self, other: Any) -> bool:
        if isinstance(other, Minecraft):
            return self.__mc_gameVersion == other.__mc_gameVersion and self.__mc_gameWorkDir == other.__mc_gameWorkDir and self.__mc_gameJarFile == other.__mc_gameJarFile and self.__mc_gameJsonFile == other.__mc_gameJsonFile and self.__mc_gameNativesDir == other.__mc_gameNativesDir and self.__mc_gameAssetsDir == other.__mc_gameAssetsDir and self.__mc_gameLibrariesDir == other.__mc_gameLibrariesDir
        else:
            return False
    
    @property
    def mc_gameVersion(self) -> Optional[str]:
        return self.__mc_gameVersion
    
    @mc_gameVersion.setter
    def mc_gameVersion(self, value: Optional[str]):
        self.__mc_gameVersion = value
    
    @property
    def mc_gameWorkDir(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameWorkDir).absolute()
    
    @mc_gameWorkDir.setter
    def mc_gameWorkDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameWorkDir = Path(value).absolute()
    
    @property
    def mc_gameJarFile(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameJarFile).absolute()
    
    @mc_gameJarFile.setter
    def mc_gameJarFile(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameJarFile = Path(value).absolute()
    
    @property
    def mc_gameJsonFile(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameJsonFile).absolute()
    
    @mc_gameJsonFile.setter
    def mc_gameJsonFile(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameJsonFile = Path(value).absolute()
        self.__mc_gameJsonFileInfo = None
        if Path(self.__mc_gameJsonFile).is_file() and Path(self.__mc_gameJsonFile).suffix == ".json":
            self.__mc_gameJsonFileInfo = json.loads(Path(self.__mc_gameJsonFile).read_text(encoding="utf-8"))
            if self.__mc_gameJsonFileInfo:
                self.__mc_gameAssetsIndex = self.__mc_gameJsonFileInfo.get("assets")
            else:
                self.__mc_gameAssetsIndex = None
    
    @property
    def mc_gameJsonFileInfo(self) -> Optional[Union[str, dict]]:
        return self.__mc_gameJsonFileInfo
    
    @property
    def mc_gameNativesDir(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameNativesDir).absolute()
    
    @mc_gameNativesDir.setter
    def mc_gameNativesDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameNativesDir = Path(value).absolute()
    
    @property
    def mc_gameAssetsDir(self) -> Union[str, Path, PurePath, os.PathLike, LiteralString]:
        return Path(self.__mc_gameAssetsDir).absolute()
    
    @mc_gameAssetsDir.setter
    def mc_gameAssetsDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameAssetsDir = Path(value).absolute()
        if self.__mc_gameJsonFileInfo:
            self.__mc_gameAssetsIndex = self.__mc_gameJsonFileInfo.get("assets")
        else:
            self.__mc_gameAssetsIndex = None
    
    @property
    def mc_gameAssetsIndex(self) -> Optional[str]:
        return self.__mc_gameAssetsIndex
    
    @property
    def mc_gameLibrariesDir(self) -> Union[str, Path, PurePath, os.PathLike, LiteralString]:
        return Path(self.__mc_gameLibrariesDir).absolute()
    
    @mc_gameLibrariesDir.setter
    def mc_gameLibrariesDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameLibrariesDir = Path(value).absolute()
