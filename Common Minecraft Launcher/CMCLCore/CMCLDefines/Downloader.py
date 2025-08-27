# -*- coding: utf-8 -*-
import os
from typing import *

import requests
from dataclasses import dataclass
from pathlib import Path, PurePath
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.message import EmailMessage


class Downloader:
    @dataclass(frozen=True)
    class ChunkData:
        startPosition: int
        responseContent: bytes
    
    def __init__(
            self,
            download_url: Union[str, LiteralString],
            download_file_name: Union[str, Path, PurePath, os.PathLike, LiteralString] = "",
            download_file_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
            maximum_threads: Union[int, str] = 64,
            chunk_size: Union[int, str] = 1024 * 1024 * 8
    ):
        self.download_url = str(download_url)
        self.download_file_name = Path(download_file_name)
        self.download_file_path = Path(download_file_path)
        self.__maximumThreads = int(maximum_threads)
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
        
        if requestHeaders.get("Content-Disposition"):
            dispositions = requestHeaders.get("Content-Disposition")
            msg = EmailMessage()
            msg['Content-Disposition'] = dispositions
            params = msg["Content-Disposition"].params
            if not self.download_file_name:
                self.download_file_name = params["filename"]
        
        rangeRequestState = requestHeaders.get("Accept-Ranges", "none").lower()
        if rangeRequestState != "none":
            contentLength = int(requestHeaders.get("Content-Length", 0))
            with ThreadPoolExecutor(max_workers=self.maximumThreads) as executor:
                startPosition = 0
                while startPosition < contentLength:
                    downloadedChunks.append(
                        executor.submit(
                            self.__downloadChunk,
                            startPosition,
                            min(startPosition + self.__chunkSize, contentLength)
                        )
                    )
                    startPosition += self.__chunkSize
            downloadedChunks = [future.result() for future in as_completed(downloadedChunks)]
        else:
            with requests.get(self.download_url, stream=True) as response:
                response.raise_for_status()
                downloadedChunks.append(self.ChunkData(startPosition=0, responseContent=response.content))
        self.download_file_path.mkdir(parents=True, exist_ok=True)
        with Path(self.download_file_path / self.download_file_name).absolute().open(mode="wb") as file:
            for chunkData in downloadedChunks:
                file.seek(chunkData.startPosition)
                file.write(chunkData.responseContent)
    
    def __downloadChunk(
            self,
            start_point: int,
            end_point: int
    ) -> 'Downloader.ChunkData':
        response = requests.get(
            self.download_url,
            headers={
                "Range": f"bytes={int(start_point)}-{int(end_point) - 1}",
                "Accept-Encoding": "identity"
            }
        )
        response.raise_for_status()
        return self.ChunkData(
            startPosition=int(start_point),
            responseContent=response.content
        )
    
    def __enter__(self) -> 'Downloader':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
