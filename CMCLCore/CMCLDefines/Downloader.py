# -*- coding: utf-8 -*-
import os
from typing import *

import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path, PurePath
from queue import Queue


class Downloader:
    def __init__(
            self,
            download_url: Union[str, LiteralString],
            download_file_name: Union[str, Path, PurePath, os.PathLike, LiteralString],
            download_file_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
            maximum_threads: Union[int, str] = 64,
            chunk_size: Union[int, str, Decimal] = 1024
    ):
        self.download_url = str(download_url)
        self.download_file_name = Path(download_file_name)
        self.download_file_path = Path(download_file_path)
        self.__maximumThreads = int(maximum_threads)
        self.__chunkSize = Decimal(str(chunk_size))
    
    @property
    def maximumThreads(self) -> Union[int, str]:
        return self.__maximumThreads
    
    @maximumThreads.setter
    def maximumThreads(self, value: Union[int, str]):
        self.__maximumThreads = int(value)
    
    @property
    def chunkSize(self) -> Union[int, str, Decimal]:
        return self.__chunkSize
    
    @chunkSize.setter
    def chunkSize(self, value: Union[int, str, Decimal]):
        self.__chunkSize = Decimal(str(value))
    
    def downloadFile(
            self,
            maximum_threads: Optional[Union[int, str]] = None,
            chunk_size: Union[int, str, Decimal] = None
    ):
        if maximum_threads:
            self.maximumThreads = int(maximum_threads)
        if chunk_size:
            self.chunkSize = Decimal(str(chunk_size))
        chunks = Queue()
        rangeRequestState = requests.head(self.download_url).headers.get("Accept-Range", "none").lower()
        if rangeRequestState != "none":
            contentLength = Decimal(str(requests.head(self.download_url).headers.get("Content-Length", 0)))
            with ThreadPoolExecutor(max_workers=self.maximumThreads) as executor:
                futures = []
                startPosition = Decimal("0")
                while startPosition < contentLength + int(contentLength % self.__chunkSize):
                    futures.append(
                        executor.submit(
                            self.__downloadChunk,
                            self.download_url,
                            startPosition,
                            min(startPosition + self.__chunkSize, contentLength)
                        )
                    )
                    startPosition += self.__chunkSize
                
                for future in as_completed(futures):
                    chunks.put(future.result())
        else:
            content = requests.get(self.download_url).content
            chunks.put({"StartPosition": 0, "EndPosition": len(content), "ResponseContent": content})
        with Path(self.download_file_path / self.download_file_name).open(mode="ab") as file:
            for chunk in range(chunks.qsize()):
                responseData = chunks.get()
                file.seek(responseData["StartPosition"])
                file.write(responseData["ResponseContent"])
    
    @staticmethod
    def __downloadChunk(
            download_url: Union[str, LiteralString],
            start_point: Union[int, float, Decimal],
            end_point: Union[int, float, Decimal]
    ):
        response = requests.get(download_url, headers={"Range": f"bytes={int(start_point)}-{int(end_point)}"},
                                stream=True, verify=True)
        if response.status_code == 206:
            return {
                "StartPosition": start_point,
                "EndPosition": end_point,
                "ResponseContent": response.content
            }
        return {
            "StartPosition": 0,
            "EndPosition": response.headers.get("Content-Length", 0),
            "ResponseContent": requests.get(download_url, stream=True, verify=True).content
        }
