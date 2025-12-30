# -*- coding: utf-8 -*-
import json
from pathlib import Path


def createSettingsFile():
    Path(".settings.json").write_text(json.dumps({
        "Settings": {
            "LaunchSettings": {
                "Java": {
                    "AutoSelect": True,
                    "JavaPath": None,
                    "JVM": {
                        "OverrideDefault": False,
                        "JVMArguments": {
                            "Arguments": None
                        }
                    }
                },
                "ExtraGameCommand": None,
                "VersionSeparation": 0,
                "VersionSeparationConfig": {
                    "ShareVersionOptions": False,
                    "ShareVersionResourcePacks": False
                }
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
    }, indent=4), encoding="utf-8")


def createVersionConfigFile(file_path, version_name, version_path):
    Path(file_path / "version.cfg").write_text(json.dumps({
        "Version": version_name,
        "VersionAlias": version_path,
        "LaunchConfig": {
            "SyncWithDefault": True
        }
    }, indent=4))


def loadSettingsFile():
    file = Path(".settings.json")
    if not file.exists():
        createSettingsFile()
    return json.loads(file.read_text(encoding="utf-8"))


def loadSettings():
    return loadSettingsFile()["Settings"]


def saveSettings(settings):
    fileJson = loadSettingsFile()
    fileJson["Settings"] = settings
    saveSettingsFile(fileJson)


def saveSettingsFile(content):
    Path(".settings.json").write_text(json.dumps(content, indent=4), encoding="utf-8")


def loadVersionConfig(file_path):
    return json.loads(Path(file_path).read_text(encoding="utf-8"))
