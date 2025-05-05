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
    def maximum_threads(self):
        return self.maximum_threads
    
    @property
    def chunk_size(self):
        return self.chunk_size
    
    def download(
            self,
            maximum_threads: Optional[Union[int, str]] = None,
            chunk_size: Union[int, str, Decimal] = None
    ):
        if maximum_threads:
            self.__maximumThreads = int(maximum_threads)
        if chunk_size:
            self.__chunkSize = Decimal(str(chunk_size))
        chunks = Queue()
        rangeRequestState = requests.head(self.download_url).headers.get("Accept-Range", "none").lower()
        if rangeRequestState != "none":
            contentLength = Decimal(str(requests.head(self.download_url).headers.get("Content-Length", 0)))
            with ThreadPoolExecutor(max_workers=self.__maximumThreads) as executor:
                futures = []
                startPosition = Decimal("0")
                while startPosition < contentLength + int(contentLength % self.__chunkSize):
                    futures.append(
                        executor.submit(self.__download_chunk, self.download_url, startPosition,
                                        min(startPosition + self.__chunkSize, contentLength)))
                    startPosition += self.__chunkSize
                
                for future in as_completed(futures):
                    chunks.put(future.result())
        else:
            content = requests.get(self.download_url).content
            chunks.put({"Start": 0, "End": len(content), "Content": content})
        with Path(self.download_file_path / self.download_file_name).open(mode="ab") as file:
            for chunk in range(chunks.qsize()):
                response_data = chunks.get()
                file.seek(response_data["Start"])
                file.write(response_data["Content"])
    
    @staticmethod
    def __download_chunk(
            download_url: Union[str, LiteralString],
            start_point: Union[int, float, Decimal],
            end_point: Union[int, float, Decimal]
    ):
        headers = {"Range": f"bytes={int(start_point)}-{int(end_point)}"}
        response = requests.get(download_url, headers=headers, stream=True, verify=True)
        if response.status_code == 206:
            return {
                "Start": start_point,
                "End": end_point,
                "Content": response.content
            }
        return {
            "Start": 0,
            "End": response.headers.get("Content-Length", 0),
            "Content": requests.get(download_url, stream=True, verify=True).content
        }
