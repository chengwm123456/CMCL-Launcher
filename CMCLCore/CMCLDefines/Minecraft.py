# -*- coding: utf-8 -*-
from pathlib import Path, PurePath
from typing import *
import os


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
        self.__mc_gameNativesDir = None
        self.__mc_gameAssetsDir = None
        self.__mc_gameLibrariesDir = None
        if game_version:
            self.__mc_gameVersion = game_version
        if Path(game_work_dir).is_dir():
            self.__mc_gameWorkDir = PurePath(game_work_dir)
        if Path(game_jar).is_file() and Path(game_jar).suffix == ".jar":
            self.__mc_gameJarFile = PurePath(game_jar)
        if Path(game_json).is_file() and Path(game_json).suffix == ".json":
            self.__mc_gameJsonFile = PurePath(game_json)
        if Path(game_natives_dir).is_dir():
            self.__mc_gameNativesDir = PurePath(game_natives_dir)
        if Path(game_asset_dir).is_dir():
            self.__mc_gameAssetsDir = PurePath(game_asset_dir)
        if Path(game_libs).is_dir():
            self.__mc_gameLibrariesDir = PurePath(game_libs)
    
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
            return eval(f"self.__mc_{item}")
        finally:
            pass
    
    def __setitem__(self, key: str, value: Any):
        exec(f"self.__mc_{key} = {value}")
    
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
        return self.__mc_gameWorkDir
    
    @mc_gameWorkDir.setter
    def mc_gameWorkDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameWorkDir = value
    
    @property
    def mc_gameJarFile(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return self.__mc_gameJarFile
    
    @mc_gameJarFile.setter
    def mc_gameJarFile(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameJarFile = value
    
    @property
    def mc_gameJsonFile(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return self.__mc_gameJsonFile
    
    @mc_gameJsonFile.setter
    def mc_gameJsonFile(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameJsonFile = value
    
    @property
    def mc_gameNativesDir(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return self.__mc_gameNativesDir
    
    @mc_gameNativesDir.setter
    def mc_gameNativesDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameNativesDir = value
    
    @property
    def mc_gameAssetsDir(self) -> Union[str, Path, PurePath, os.PathLike, LiteralString]:
        return self.__mc_gameAssetsDir
    
    @mc_gameAssetsDir.setter
    def mc_gameAssetsDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameAssetsDir = value
    
    @property
    def mc_gameLibrariesDir(self) -> Union[str, Path, PurePath, os.PathLike, LiteralString]:
        return self.__mc_gameLibrariesDir
    
    @mc_gameLibrariesDir.setter
    def mc_gameLibrariesDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameLibrariesDir = value
