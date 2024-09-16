# -*- coding: utf-8 -*-
from pathlib import Path
from typing import *
import os


class Minecraft:
    def __init__(self, version: str = "", game_work_dir: Union[str, Path, os.PathLike, LiteralString] = "",
                 game_jar: Union[str, Path, os.PathLike, LiteralString] = "",
                 game_json: Union[str, Path, os.PathLike, LiteralString] = "",
                 game_asset: Union[str, Path, os.PathLike, LiteralString] = "",
                 game_libs: Union[str, Path, os.PathLike, LiteralString] = ""):
        self.__mc_jarPath = None
        self.__mc_version = None
        self.__mc_json = None
        if Path(game_jar).is_file():
            self.__mc_jarPath = Path(game_json)
        if Path(game_json).is_file():
            self.__mc_json = Path(game_json)
        else:
            self.__mc_json = Path(self.__mc_jarPath.parent / f"{self.__mc_version}.json")
        if Path(game_work_dir).is_dir():
            self._mc_workDir = Path(game_work_dir)
        if version:
            self.__mc_version = version
