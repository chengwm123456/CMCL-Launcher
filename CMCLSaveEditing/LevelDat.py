# -*- coding: utf-8 -*-
from .NbtBase import LoadFile, EditKey


def LoadLevelDat(level_dat):
    return LoadFile(level_dat)


def LoadData(level_dat):
    return LoadLevelDat(level_dat)["Data"]
