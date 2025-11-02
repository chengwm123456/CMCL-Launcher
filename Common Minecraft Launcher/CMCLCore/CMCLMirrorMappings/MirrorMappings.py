# -*- coding: utf-8 -*-
import json
from enum import IntEnum
from pathlib import Path
from urllib.parse import urlparse, urlunparse


class MirrorSourceName(IntEnum):
    BMCLAPI = 0


mapping_route = Path("")
if __name__ != "main":
    mapping_route = Path(__file__).parent

bmclapi_url_mappings = json.loads((mapping_route / "BMCLAPI.json").read_text(encoding="utf-8"))

url_mappings = (bmclapi_url_mappings,)

globals()["mirrorSourceEnabled"] = False
globals()["mirrorSources"] = []


def MirrorSourceEnabled(enabled=None, name=None):
    if enabled is None:
        return globals()["mirrorSourceEnabled"]
    if enabled:
        globals()["mirrorSourceEnabled"] = True
        name = name if isinstance(name, int) else name.value
        if name in globals()["mirrorSources"]:
            pass
        else:
            globals()["mirrorSources"].append(name)
    else:
        globals()["mirrorSourceEnabled"] = False
        globals()["mirrorSources"] = []


def GetMirrorSourceMappings(url=None):
    if globals()["mirrorSourceEnabled"]:
        mappings = {}
        for mapping in globals()["mirrorSources"]:
            mappings.update(url_mappings[mapping])
        if not url:
            return mappings
        return mappings.get(url, url)
    return url


def GetMirrorSourceUrl(url=None):
    if not url:
        return
    if globals()["mirrorSourceEnabled"]:
        urlparsed = list(urlparse(url))
        urlparsed[1] = GetMirrorSourceMappings(urlparsed[1])
        url = urlunparse(urlparsed)
    return url
