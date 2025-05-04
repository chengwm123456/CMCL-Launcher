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
        self.__mc_gameNativesDir = None
        self.__mc_gameAssetsDir = None
        self.__mc_gameLibrariesDir = None
        if game_version:
            self.__mc_gameVersion = game_version
        if Path(game_work_dir).is_dir():
            self.__mc_gameWorkDir = Path(game_work_dir).absolute()
        if Path(game_jar).is_file() and Path(game_jar).suffix == ".jar":
            self.__mc_gameJarFile = Path(game_jar).absolute()
        if Path(game_json).is_file() and Path(game_json).suffix == ".json":
            self.__mc_gameJsonFile = Path(game_json).absolute()
        if Path(game_natives_dir).is_dir():
            self.__mc_gameNativesDir = Path(game_natives_dir).absolute()
        if Path(game_asset_dir).is_dir():
            self.__mc_gameAssetsDir = Path(game_asset_dir).absolute()
        if Path(game_libs).is_dir():
            self.__mc_gameLibrariesDir = Path(game_libs).absolute()
    
    def __iter__(self) -> Iterable[Any]:
        for item in (self.__mc_gameVersion, self.__mc_gameWorkDir, self.__mc_gameJarFile, self.__mc_gameJsonFile,
                     self.__mc_gameNativesDir, self.__mc_gameAssetsDir, self.__mc_gameLibrariesDir):
            yield item
    
    def __bool__(self) -> bool:
        return any(tuple(self.__iter__()))
    
    def __getitem__(self, item: str) -> Optional[Any]:
        return self.__getattribute__(item)
    
    def __setitem__(self, key: str, value: Optional[Any]):
        self.__setattr__(key, value)
    
    def __cmp__(self, other: Any) -> bool:
        if isinstance(other, Minecraft):
            return tuple(self.__iter__()) == tuple(other.__iter__())
        else:
            return super().__cmp__(other)
    
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
    
    @property
    def mc_gameJsonFileContent(self) -> Optional[Union[str, dict]]:
        if self.__mc_gameJsonFile and Path(self.__mc_gameJsonFile).exists():
            try:
                return json.loads(Path(self.__mc_gameJsonFile).read_text(encoding="utf-8"))
            finally:
                return None
        return None
    
    @property
    def mc_gameMainClass(self) -> Optional[str]:
        return (self.mc_gameJsonFileContent or {}).get("mainClass")
    
    @property
    def mc_gameNativesDir(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameNativesDir).absolute()
    
    @mc_gameNativesDir.setter
    def mc_gameNativesDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameNativesDir = Path(value).absolute()
    
    @property
    def mc_gameAssetsDir(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameAssetsDir).absolute()
    
    @mc_gameAssetsDir.setter
    def mc_gameAssetsDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameAssetsDir = Path(value).absolute()
    
    @property
    def mc_gameAssetsIndex(self) -> Optional[str]:
        return (self.mc_gameJsonFileContent or {}).get("assets")
    
    @property
    def mc_gameLibrariesDir(self) -> Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]]:
        return Path(self.__mc_gameLibrariesDir).absolute()
    
    @mc_gameLibrariesDir.setter
    def mc_gameLibrariesDir(self, value: Union[str, Path, PurePath, os.PathLike, LiteralString]):
        self.__mc_gameLibrariesDir = Path(value).absolute()
    
    @property
    def mc_gameLibrariesFiles(self) -> Iterable[Any]:
        return (self.mc_gameJsonFileContent or {}).get("libraries", [])
