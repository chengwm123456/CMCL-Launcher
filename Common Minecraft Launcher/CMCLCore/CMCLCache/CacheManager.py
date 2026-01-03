# -*- coding: utf-8 -*-
from typing import Any, Hashable, Optional, Union

import os
import time
import json
from dataclasses import dataclass
from pathlib import Path


class CacheManager:
    @dataclass
    class Cache:
        age: int = 0
        start: int = 0
        content: Any = None
        
        @classmethod
        def fromJSON(cls, json_data: dict):
            return cls(**json_data)
        
        def toJSON(self):
            return {"age": self.age, "start": self.start, "content": self.content}
    
    def __init__(self, storeFile: Optional[Union[str, os.PathLike]] = None):
        self.caches = {}
        if storeFile and Path(storeFile).is_file():
            tmpCache = {}
            try:
                tmpCache = json.loads(Path(storeFile).read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                tmpCache = {}
            for key in tmpCache:
                self.caches[key] = self.Cache.fromJSON(tmpCache[key])
    
    def getCache(self, key: Hashable):
        cache = self.caches.get(key)
        if not cache:
            return None
        if cache.age > 0 and cache.start + cache.age <= time.time():
            del self.caches[key]
            return None
        return cache.content
    
    def setCache(self, key: Hashable, value: Any = None, age: int = 60):
        cache = self.Cache(age=age, start=int(time.time()), content=value)
        self.caches[key] = cache
    
    def clearCache(self):
        self.caches.clear()
    
    def storeCache(self, filename: Optional[Union[str, os.PathLike]] = None) -> Path:
        result = {}
        for cache in self.caches:
            result[cache] = self.caches[cache].toJSON()
        if not filename:
            if os.name == "nt":
                filename = Path(os.environ.get("TEMP")) / ".cache.json"
            else:
                filename = Path("/tmp/.cache.json")
        Path(filename).write_text(json.dumps(result, indent=1), encoding="utf-8")
        return Path(filename)
    
    def __getitem__(self, key: Hashable):
        return self.getCache(key)
    
    def __setitem__(self, key: Hashable, value: Any):
        self.setCache(key, value)
