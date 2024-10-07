# -*- coding: utf-8 -*-
from pathlib import Path
from typing import *
import os
import subprocess


class Minecraft:
    def __init__(
            self,
            version: str = "",
            game_work_dir: Union[str, Path, os.PathLike, LiteralString] = "",
            game_jar: Union[str, Path, os.PathLike, LiteralString] = "",
            game_json: Union[str, Path, os.PathLike, LiteralString] = "",
            game_asset_dir: Union[str, Path, os.PathLike, LiteralString] = "",
            game_libs: Union[str, Path, os.PathLike, LiteralString] = "",
            game_config: Union[str, Path, os.PathLike, LiteralString] = "",
            launch_jvm_config: Optional[dict] = None,
            launch_cmd_config: Optional[dict] = None,
    ):
        self.__mc_version = None
        self.__mc_workDir = None
        self.__mc_jarPath = None
        self.__mc_version = None
        self.__mc_json = None
        self.__mc_asset_dir = None
        self.__mc_libs = None
        self.__mc_gameCfg = None
        if version:
            self.__mc_version = version
        if Path(game_work_dir).is_dir():
            self.__mc_workDir = Path(game_work_dir)
        if Path(game_jar).is_file() and Path(game_jar).suffix == ".jar":
            self.__mc_jarPath = Path(game_json)
        if Path(game_json).is_file() and Path(game_json).suffix == ".json":
            self.__mc_json = Path(game_json)
        if Path(game_asset_dir).is_dir():
            self.__mc_asset_dir = Path(game_asset_dir)
        if Path(game_libs).is_dir():
            self.__mc_libs = Path(game_libs)
        if Path(game_config).is_file():
            self.__mc_gameCfg = Path(game_config)
    
    def __iter__(self) -> Iterable[Union[Any]]:
        yield self.__mc_version
        yield self.__mc_workDir
        yield self.__mc_jarPath
        yield self.__mc_json
        yield self.__mc_asset_dir
        yield self.__mc_libs
        yield self.__mc_gameCfg
    
    def __bool__(self) -> bool:
        return bool(
            self.__mc_version and self.__mc_workDir and self.__mc_jarPath and self.__mc_json and self.__mc_asset_dir and self.__mc_libs and self.__mc_gameCfg)
    
    def __getitem__(self, item: str) -> Optional[Any]:
        try:
            return eval(f"self.__mc_{item}")
        finally:
            pass
    
    def __setitem__(self, key: str, value: Any):
        exec(f"self.__mc_{key} = {value}")
    
    def __cmp__(self, other: Any) -> bool:
        if isinstance(other, Minecraft):
            return self.__mc_version == other.__mc_version and self.__mc_workDir == other.__mc_workDir and self.__mc_jarPath == other.__mc_jarPath and self.__mc_json == other.__mc_json and self.__mc_asset_dir == other.__mc_asset_dir and self.__mc_libs == other.__mc_libs and self.__mc_gameCfg == other.__mc_gameCfg
        else:
            return False
