# -*- coding: utf-8 -*-
from .DataClasses import Mod


def GetModIcon(mod):
    content = None
    with mod.getZipFile() as file:
        cfg = mod.getModInfo()
        if cfg.get("icon"):
            content = file.read(cfg.get("icon"))
    
    return content


def GetModTranslations(mod):
    return []
