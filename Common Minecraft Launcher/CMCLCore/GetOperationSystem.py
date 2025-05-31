# -*- coding: utf-8 -*-
import platform
from typing import *


def GetOperationSystemName() -> Tuple[str, str]:
    system = platform.system()
    if system == "Darwin":
        system = "Mac OS"
    return system, platform.machine()


def GetOperationSystemInMojangApi() -> Tuple[str, str]:
    system = platform.system()
    if system == "Darwin":
        system = "Mac OS"
    current_machine = platform.machine()[-2:]
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
