# -*- coding: utf-8 -*-
import os
from typing import *

import requests
from dataclasses import dataclass
from pathlib import Path, PurePath
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.message import EmailMessage

import gzip
import zlib
import zstandard as zstd


class Downloader:
    @dataclass(frozen=True)
    class Range:
        startRange: int = 0
        endRange: int = 0
    
    @dataclass(frozen=True)
    class DownloadedChunk:
        chunkRange: 'Downloader.Range'
        contentEncoding: Optional[str]
        responseContent: bytes
    
    def __init__(
            self,
            download_url: Union[str, LiteralString],
            download_file_name: Optional[Union[str, Path, PurePath, os.PathLike, LiteralString]] = "",
            download_file_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
            maximum_threads: Union[int, str] = 8,
            chunk_size: Union[int, str] = 1024 * 1024 * 8
    ):
        self.download_url = str(download_url)
        if download_file_name:
            self.download_file_name = Path(download_file_name)
        else:
            self.download_file_name = None
        self.download_file_path = Path(download_file_path).resolve()
        self.__maximumThreads = int(maximum_threads or 8)
        self.__chunkSize = max(1024, int(chunk_size))
    
    @property
    def maximumThreads(self) -> Union[int, str]:
        return self.__maximumThreads
    
    @maximumThreads.setter
    def maximumThreads(self, value: Union[int, str]):
        self.__maximumThreads = int(value)
    
    @property
    def chunkSize(self) -> Union[int, str]:
        return self.__chunkSize
    
    @chunkSize.setter
    def chunkSize(self, value: Union[int, str]):
        self.__chunkSize = int(value)
    
    def downloadFile(
            self,
            maximum_threads: Optional[Union[int, str]] = None,
            chunk_size: Optional[Union[int, str]] = None
    ):
        if maximum_threads:
            self.maximumThreads = int(maximum_threads)
        if chunk_size:
            self.chunkSize = int(chunk_size)
        downloadedChunks = []
        with requests.head(self.download_url) as headResponse:
            headResponse.raise_for_status()
            requestHeaders = headResponse.headers
            
            if not (requestHeaders.get("Accept-Ranges") or requestHeaders.get("Content-Length")):
                with requests.get(self.download_url, headers={"Range": "bytes=0-0"}) as headResponse:
                    headResponse.raise_for_status()
                    requestHeaders = headResponse.headers
        
        contentLength = int(requestHeaders.get("Content-Length", 0))
        
        if requestHeaders.get("Content-Disposition"):
            msg = EmailMessage()
            msg["Content-Disposition"] = requestHeaders.get("Content-Disposition")
            params = msg["Content-Disposition"].params
            print(params, self.download_file_name, bool(self.download_file_name))
            if not self.download_file_name and params.get("filename"):
                self.download_file_name = Path(params["filename"])
        
        if not self.download_file_name:
            raise ValueError("Cannot leave filename blank while no `Content-Disposition` is in header")
        
        acceptRanges = requestHeaders.get("Accept-Ranges", "none").lower()
        if acceptRanges != "none":
            with ThreadPoolExecutor(max_workers=self.maximumThreads) as executor:
                startPosition = 0
                while startPosition < contentLength:
                    downloadedChunks.append(
                        executor.submit(
                            self.__downloadChunk,
                            range=self.Range(startPosition, min(startPosition + self.__chunkSize, contentLength))
                        )
                    )
                    startPosition += self.__chunkSize
            downloadedChunks = [future.result() for future in as_completed(downloadedChunks)]
        else:
            with requests.get(self.download_url, stream=True) as response:
                response.raise_for_status()
                startPosition = 0
                for chunk in response.iter_content(chunk_size=self.__chunkSize):
                    if chunk:
                        downloadedChunks.append(
                            self.DownloadedChunk(
                                chunkRange=self.Range(startPosition,
                                                      min(startPosition + self.__chunkSize, contentLength)),
                                responseContent=chunk
                            )
                        )
                        startPosition += self.__chunkSize
        self.download_file_path.mkdir(parents=True, exist_ok=True)
        with Path(self.download_file_path / self.download_file_name).resolve().open(mode="wb") as file:
            for chunkData in downloadedChunks:
                file.seek(chunkData.chunkRange.startRange)
                file.write(self.decompress(chunkData.responseContent, chunkData.contentEncoding))
    
    def __downloadChunk(
            self,
            range: 'Downloader.Range'
    ) -> 'Downloader.DownloadedChunk':
        with requests.get(
                self.download_url,
                headers={
                    "Range": f"bytes={int(range.startRange)}-{int(range.endRange) - 1}",
                    "Accept-Encoding": "gzip, deflate, zstd, identity"
                }
        ) as response:
            response.raise_for_status()
            content = response.content
            return self.DownloadedChunk(
                chunkRange=range,
                contentEncoding=response.headers.get("Content-Encoding"),
                responseContent=content
            )
    
    def decompress(self, content: bytes, encoding: Optional[str] = None) -> bytes:
        match encoding:
            case "gzip":
                return gzip.decompress(content)
            case "deflate":
                return zlib.decompress(content)
            case "zstd":
                return zstd.ZstdDecompressor().decompress(content)
            case _:
                return content
    
    def __enter__(self) -> 'Downloader':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.downloadFile()
