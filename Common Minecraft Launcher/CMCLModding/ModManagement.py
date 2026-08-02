# -*- coding: utf-8 -*-
import json
from pathlib import Path

from .DataClasses import Mod, Loader


# Note: Identification uses the "library" key of the json file. This may return an incorrect result.
def GetLoader(minecraft_path, version):
    minecraft_path = Path(minecraft_path)

    file_data = json.loads(Path(minecraft_path / "versions" / version / f"{version}.json").read_text(encoding="utf-8"))

    try:
        if file_data["libraries"][-1]["url"] == "https://maven.fabricmc.net/":
            return Loader(loaderType="Fabric", inheritsFrom=version)
        if file_data["libraries"][-1]["url"] == "https://maven.quiltmc.org/repository/release/":
            return Loader(loaderType="Quilt", inheritsFrom=version)
        return None
    except KeyError:
        return None


def GetLoaderType(minecraft_path, version):
    loader = GetLoader(minecraft_path, version)
    if loader:
        return loader.loaderType
    else:
        return None


def ListMods(minecraft_path=None):
    if not minecraft_path:
        minecraft_path = "."
    minecraft_path = Path(minecraft_path)
    mods_path = minecraft_path / "mods"
    if not mods_path.exists():
        return tuple()
    for file in mods_path.iterdir():
        if file.suffix == ".jar":
            yield Mod(modFile=file, isEnabled=True)
        elif file.suffixes[-2:] == [".jar", ".disabled"]:
            yield Mod(modFile=file, isEnabled=False)
