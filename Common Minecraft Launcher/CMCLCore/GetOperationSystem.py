# -*- coding: utf-8 -*-
import platform
from typing import *


def GetOperationSystemName() -> str:
    system = platform.system()
    if system == "Darwin":
        system = "Mac OS"
    return system


def GetOperationSystemMachine() -> str:
    return platform.machine()


def GetOperationSystem() -> Tuple[str, str]:
    return GetOperationSystemName(), GetOperationSystemMachine()


def GetOperationSystemInMojangAPI() -> Tuple[str, str]:
    name = GetOperationSystem()
    system = name[0]
    current_machine = name[1][-2:]
    current_system = "Unknown System"
    if system == "Windows":
        current_system = "windows"
        if current_machine == "64":
            current_machine = "64"
        else:
            current_machine = "86"
    if system == "Mac OS":
        current_system = "osx"
    if system == "Linux":
        current_system = "linux"
    return current_system, f"x{current_machine}"
