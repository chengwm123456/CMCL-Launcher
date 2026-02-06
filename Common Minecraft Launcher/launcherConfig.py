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


def createVersionConfigFile(file_path, version_name, version_path):
    Path(file_path / "version.cfg").write_text(yaml.dump({
        "Version": version_name,
        "VersionAlias": version_path,
        "LaunchConfig": {
            "SyncWithDefault": True
        }
    }, allow_unicode=True, indent=2))


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


def loadVersionConfig(file_path):
    return yaml.safe_load(Path(file_path).read_text(encoding="utf-8"))
