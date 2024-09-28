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
            launch_config: Optional[dict, str] = None,
    ):
        self.__mc_version = None
        self.__mc_workDir = None
        self.__mc_jarPath = None
        self.__mc_version = None
        self.__mc_json = None
        self.__mc_asset_dir = None
        self.__mc_libs = None
        self.__mc_launchCfg = None
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
        if launch_config:
            self.__mc_launchCfg = dict(launch_config)
