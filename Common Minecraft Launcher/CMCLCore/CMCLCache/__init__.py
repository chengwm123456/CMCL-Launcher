# -*- coding: utf-8 -*-
from .CacheManager import CacheManager

if not globals().get("cacheManager"):
    globals()["cacheManager"] = CacheManager()


def getCache(key):
    return globals()["cacheManager"].getCache(key)


def setCache(key, value, age=60):
    globals()["cacheManager"].setCache(key, value, age)
