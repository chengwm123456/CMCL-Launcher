# -*- coding: utf-8 -*-
import platform
from typing import *


def GetOperationSystemName(lower=False) -> str:
    system = platform.system()
    if lower:
        return system.lower()
    return system


def GetOperationSystemMachine() -> str:
    return platform.machine()


def GetOperationSystem(lower=False) -> Tuple[str, str]:
    return GetOperationSystemName(lower), GetOperationSystemMachine()


def GetOperationSystemInMojangAPI() -> Tuple[str, str]:
    name = GetOperationSystem()
    system = name[0]
    current_machine = name[1][-2:]
    current_system = ""
    if system == "Windows":
        current_system = "windows"
        if current_machine == "64":
            current_machine = "64"
        else:
            current_machine = "86"
    if system == "Darwin":
        current_system = "osx"
    if system == "Linux":
        current_system = "linux"
    return current_system, f"x{current_machine}"
