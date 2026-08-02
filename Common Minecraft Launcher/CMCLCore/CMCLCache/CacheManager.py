# -*- coding: utf-8 -*-
from typing import Any, Hashable, Optional, Union

import os
import time
import json
from dataclasses import dataclass
from pathlib import Path
import pickle


class CacheManager:
    @dataclass(frozen=True)
    class Cache:
        age: int = 0
        start: int = 0
        content: Any = None
    
    def __init__(self, storeFile: Optional[Union[str, os.PathLike]] = None):
        self.caches = {}
        if storeFile and Path(storeFile).is_file():
            self.loadCache(storeFile)
    
    def getCache(self, key: Hashable):
        cache = self.caches.get(key)
        if not cache:
            return None
        if cache.age > 0 and cache.start + cache.age <= time.time():
            del self.caches[key]
            return None
        return cache.content
    
    def setCache(self, key: Hashable, value: Any = None, age: int = 60):
        if value is None:
            del self.caches[key]
            return
        self.caches[key] = self.Cache(age=age, start=int(time.time()), content=value)
    
    def clearCache(self):
        self.caches.clear()
    
    def storeCache(self, filename: Optional[Union[str, os.PathLike]] = None) -> Path:
        if not filename:
            if os.name == "nt":
                filename = Path(os.environ.get("TEMP")) / ".cache.bin"
            else:
                filename = Path("/tmp/.cache.bin")
        Path(filename).write_bytes(pickle.dumps(self.caches))
        return Path(filename)
    
    def loadCache(self, filename: Optional[Union[str, os.PathLike]] = None):
        if not filename:
            if os.name == "nt":
                filename = Path(os.environ.get("TEMP")) / ".cache.bin"
            else:
                filename = Path("/tmp/.cache.bin")
        self.caches = pickle.loads(filename.read_bytes())
        return Path(filename)
    
    def __getitem__(self, key: Hashable):
        return self.getCache(key)
    
    def __setitem__(self, key: Hashable, value: Any):
        self.setCache(key, value)
    
    def __len__(self, key):
        expired = 0
        for value in self.caches.values():
            if value.start + value.age <= time.time():
                expired += 1
        return len(self.caches) - expired
    
    def __contains__(self, key):
        return key in self.caches and not (self.caches[key].start + self.caches[key].age <= time.time())
