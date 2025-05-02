# -*- coding: utf-8 -*-
from typing import *
from pathlib import Path


def GenerateFileNameByNames(names: Union[str, Iterable[str]]):
    if isinstance(names, str):
        names = names.split(":")
    return Path(f"{'-'.join(names[1:])}.jar")
