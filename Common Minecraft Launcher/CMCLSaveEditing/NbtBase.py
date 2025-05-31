# -*- coding: utf-8 -*-
import nbtlib


def LoadFile(file):
    return nbtlib.load(file)


def EditKey(file, key, value):
    with nbtlib.load(file) as nbt:
        nbt[key] = value
