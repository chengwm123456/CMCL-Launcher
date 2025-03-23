# -*- coding: utf-8 -*-
import os
from pathlib import Path


def ListMods(minecraft_path=None):
    if not minecraft_path:
        minecraft_path = "."
    minecraft_path = Path(minecraft_path)
    mods_path = minecraft_path / "mods"
    if not mods_path.exists():
        return ()
    return tuple(mods_path.iterdir())
