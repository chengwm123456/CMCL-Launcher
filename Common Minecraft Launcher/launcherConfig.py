# -*- coding: utf-8 -*-
# import json
from pathlib import Path
import yaml


def createSettingsFile():
    Path(".settings.yaml").write_text(yaml.dump({
        "Settings": {
            "LaunchSettings": {
                "Java": {
                    "AutoSelect": True,
                    "JavaPath": None,
                    "JVM": {
                        "JVMArguments": {
                            "Arguments": None
                        }
                    }
                },
                "ExtraGameCommand": None,
                "MemoryAllocation": {
                    "AutoAllocate": True,
                    "AllocationConfig": {
                        "InitialHeapSize": None,
                        "MaximumHeapSize": None
                    }
                },
                "VersionSeparation": 0,
                "VersionSeparationConfig": {
                    "ShareVersionOptions": False,
                    "ShareVersionResourcePacks": False
                },
                "LauncherVisibility": 0
            },
            "LauncherSettings": {
                "Personalisation": {
                    "CurrentThemePreset": "PresetBlue",
                    "CurrentTheme": "Dark",
                    "BackgroundColour": [
                        32,
                        65,
                        235
                    ]
                },
                "MinecraftPath": ".",
                "SavedMinecraftPaths": [],
                "DownloadSettings": {
                    "DownloadThreadsCount": 8,
                    "DownloadChunkSize": 1024
                },
                "Language": None
            }
        }
    }, allow_unicode=True, indent=2), encoding="utf-8")


def createVersionConfigFile(file_path, version_name, version_path, icon_path):
    Path(file_path / "version.cfg").write_text(yaml.dump({
        "Version": str(version_name),
        "VersionAlias": str(version_path),
        "Personalisation": {
            "Icon": str(icon_path)
        },
        "LaunchConfig": {
            "SyncWithDefault": True,
        }
    }, allow_unicode=True, indent=2))


def loadVersionConfig(minecraft_path, version_path):
    if not (Path(minecraft_path) / "versions" / version_path / "version.cfg").exists():
        createVersionConfigFile(Path(minecraft_path) / "versions" / version_path, version_path, version_path,
                                ":/missingno.png")
    return yaml.safe_load(
        (Path(minecraft_path) / "versions" / version_path / "version.cfg").read_text(encoding="utf-8"))


def saveVersionConfig(minecraft_path, version_path, content):
    return (Path(minecraft_path) / "versions" / version_path / "version.cfg").write_text(yaml.dump(content),
                                                                                         encoding="utf-8")


def getVersionConfig(minecraft_path, version_path, launcher_settings, keys):
    if version_path:
        versionConfig = loadVersionConfig(minecraft_path, version_path)
    else:
        versionConfig = {
            "LaunchConfig": {
                "LaunchSettings": launcher_settings["LaunchSettings"]
            }
        }
    keys = keys.split(".")
    if not len(keys) or not any(keys):
        return
    if len(keys) and keys[0] == "LaunchSettings":
        keys.pop(0)
    try:
        gameCfg = versionConfig["LaunchConfig"]["LaunchSettings"]
    except KeyError:
        gameCfg = launcher_settings["LaunchSettings"]
        # add config automatically
        versionConfig["LaunchConfig"]["LaunchSettings"] = launcher_settings["LaunchSettings"]
        saveVersionConfig(minecraft_path, version_path, versionConfig)
    launcherCfg = launcher_settings["LaunchSettings"]
    for key in keys:
        try:
            if isinstance(gameCfg, str) or isinstance(launcherCfg, str):
                raise KeyError
            gameCfg = gameCfg[key]
            launcherCfg = launcherCfg[key]
        except KeyError:
            break
    if versionConfig["LaunchConfig"].get("SyncWithDefault", True):
        return launcherCfg
    return gameCfg


def setVersionConfig(minecraft_path, version_path, launcher_settings, keys, value):
    if version_path:
        versionConfig = loadVersionConfig(minecraft_path, version_path)
    else:
        versionConfig = {
            "LaunchConfig": {
                "LaunchSettings": launcher_settings["LaunchSettings"]
            }
        }
    keys = keys.split(".")
    if not len(keys) or not any(keys):
        return
    if len(keys) and keys[0] == "LaunchSettings":
        keys.pop(0)
    try:
        gameCfg = versionConfig["LaunchConfig"]["LaunchSettings"]
    except KeyError:
        gameCfg = launcher_settings["LaunchSettings"]
        # add config automatically
        versionConfig["LaunchConfig"]["LaunchSettings"] = launcher_settings["LaunchSettings"]
        saveVersionConfig(minecraft_path, version_path, versionConfig)
    launcherCfg = launcher_settings["LaunchSettings"]
    for key in keys[:-1]:
        try:
            if isinstance(gameCfg, str) or isinstance(launcherCfg, str):
                raise KeyError
            gameCfg = gameCfg[key]
            launcherCfg = launcherCfg[key]
        except KeyError:
            break
    if versionConfig["LaunchConfig"].get("SyncWithDefault", True):
        launcherCfg[keys[-1]] = value
    else:
        gameCfg[keys[-1]] = value
    saveVersionConfig(minecraft_path, version_path, versionConfig)


def loadSettingsFile():
    file = Path(".settings.yaml")
    if not file.exists():
        createSettingsFile()
    return yaml.safe_load(file.read_text(encoding="utf-8"))


def loadSettings():
    return loadSettingsFile()["Settings"]


def saveSettings(settings):
    fileJson = loadSettingsFile()
    fileJson["Settings"] = settings
    saveSettingsFile(fileJson)


def saveSettingsFile(content):
    Path(".settings.yaml").write_text(yaml.dump(content, allow_unicode=True, indent=2), encoding="utf-8")
