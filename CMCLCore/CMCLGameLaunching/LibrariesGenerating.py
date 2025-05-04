# -*- coding: utf-8 -*-
from typing import *
import os
from pathlib import Path
from .. import GetOperationSystem


def GenerateFileNameByNames(names: Union[str, Iterable[str]]):
    if isinstance(names, str):
        names = names.split(":")
    return Path(f"{'-'.join(names[1:])}.jar")


def GenerateMinecraftLibrariesFiles(minecraft, libraries_datas):
    mcLibrariesFiles = []
    mcLibrariesFilesNames = {}
    for mcLib in libraries_datas:
        if mcLib.get("downloads"):
            if mcLib.get("rules"):
                action = "disallow"
                for rule in mcLib.get("rules", []):
                    ruleOfOS = rule.get("os", {}).get("name", GetOperationSystem.GetOperationSystemInMojangApi()[0])
                    if ruleOfOS != GetOperationSystem.GetOperationSystemInMojangApi()[0]:
                        continue
                    action = rule.get("action", action)
                allow = bool(mcLib.get("downloads", {}).get("artifact", {})) and action == "allow"
            else:
                allow = bool(mcLib.get("downloads", {}).get("artifact", {}))
            downloads = mcLib.get("downloads", {})
            if downloads.get("artifact") and allow:
                mcLibJarNames = mcLib.get("name", "::").split(":")
                mcLibJarFile = GenerateFileNameByNames(mcLibJarNames)
                mcLibPath = Path(
                    Path(mcLibJarNames[0].replace(".", os.sep)) / mcLibJarNames[1] / mcLibJarNames[
                        2] / mcLibJarFile)
                mc_lib_path_artifact = Path(minecraft.mc_gameLibrariesDir / mcLibPath)
                if len(mcLibJarNames) > 3:
                    mc_lib_name_id = tuple(mcLibJarNames[:-2] + [mcLibJarNames[-1]])
                else:
                    mc_lib_name_id = tuple(mcLibJarNames[:2])
                if mc_lib_name_id in mcLibrariesFilesNames:
                    mcLibrariesFiles[mcLibrariesFilesNames[mc_lib_name_id]] = str(mc_lib_path_artifact)
                else:
                    mcLibrariesFiles.append(str(mc_lib_path_artifact))
                mcLibrariesFilesNames[mc_lib_name_id] = len(mcLibrariesFiles) - 1
        else:
            mcLibJarNames = mcLib.get("name", ":::").split(":")
            mcLibJarFile = GenerateFileNameByNames(mcLibJarNames)
            mcLibPath = Path(
                Path(mcLibJarNames[0].replace(".", os.sep)) / mcLibJarNames[1] / mcLibJarNames[
                    2] / mcLibJarFile)
            mc_lib_path_artifact = Path(minecraft.mc_gameLibrariesDir / mcLibPath)
            if len(mcLibJarNames) > 3:
                mc_lib_name_id = tuple(mcLibJarNames[:-2] + [mcLibJarNames[-1]])
            else:
                mc_lib_name_id = tuple(mcLibJarNames[:2])
            if mc_lib_name_id in mcLibrariesFilesNames:
                mcLibrariesFiles[mcLibrariesFilesNames[mc_lib_name_id]] = str(mc_lib_path_artifact)
            else:
                mcLibrariesFiles.append(str(mc_lib_path_artifact))
            mcLibrariesFilesNames[mc_lib_name_id] = len(mcLibrariesFiles) - 1
    return mcLibrariesFiles
