# -*- coding: utf-8 -*-
import json
from pathlib import Path


# Note: Identification uses the "library" key of the json file. This may return an incorrect result.
def GetLoaderType(minecraft_path, version):
    minecraft_path = Path(minecraft_path)
    
    file_data = json.loads(Path(minecraft_path / "versions" / version / f"{version}.json").read_text(encoding="utf-8"))
    
    try:
        if file_data["libraries"][-1]["url"] == "https://maven.fabricmc.net/":
            return "Fabric"
        return None
    except KeyError:
        return None


def ListMods(minecraft_path=None):
    if not minecraft_path:
        minecraft_path = "."
    minecraft_path = Path(minecraft_path)
    mods_path = minecraft_path / "mods"
    if not mods_path.exists():
        return tuple()
    return tuple(mods_path.iterdir())
