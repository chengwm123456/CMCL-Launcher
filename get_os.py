# -*- coding: utf-8 -*-
import platform


def getOperationSystemName():
    system = platform.system()
    if system == "Darwin":
        system = "Mac OS"
    return system, platform.machine()


def get_os(**kw):
    import warnings
    warnings.warn(
        "This Function is deprecated, use function 'getOperationSystemName' or use 'getOperationSystemInMojangApi' for Mojang Api",
        DeprecationWarning)
    if kw.get("return_type", None) is not None:
        if kw["return_type"] == "MOJANG_API":
            return getOperationSystemInMojangApi()
        else:
            return getOperationSystemName()
    else:
        return getOperationSystemName()


def getOperationSystemInMojangApi():
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
