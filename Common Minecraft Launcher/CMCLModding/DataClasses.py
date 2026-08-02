# -*- coding: utf-8 -*-
from typing import Union, LiteralString, Optional
from os import PathLike
from dataclasses import dataclass

from pathlib import Path
import zipfile
import json


@dataclass(slots=True)
class Mod:
    modFile: Union[str | LiteralString | PathLike]
    isEnabled: bool
    
    def getZipFile(self):
        return zipfile.ZipFile(self.modFile, mode='r')
    
    def getModInfo(self):
        with zipfile.ZipFile(self.modFile, mode='r') as file:
            cfg = json.loads(file.read("fabric.mod.json"))
        return cfg


@dataclass(slots=True)
class Loader:
    loaderType: str
    inheritsFrom: Optional[str]
    # minecraft: Optional[Minecraft]
