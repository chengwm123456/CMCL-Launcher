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
            maximum_threads: Union[int, str] = 64, chunk_size: Union[int, str] = 1024
    ):
        self.download_url = str(download_url)
        self.download_file_name = Path(download_file_name)
        self.download_file_path = Path(download_file_path)
        self.maximum_threads = int(maximum_threads)
        self.chunk_size = Decimal(str(chunk_size))
    
    def download(self, maximum_threads: Optional[Union[int, str]] = None, chunk_size: Optional[Union[int, str]] = None):
        if maximum_threads is not None:
            self.maximum_threads = int(maximum_threads)
        if chunk_size is not None:
            self.chunk_size = Decimal(str(chunk_size))
        queue = Queue()
        range_request_state = requests.head(self.download_url).headers.get("Accept-Range", "none").lower()
        if range_request_state != "none":
            content_length = Decimal(str(requests.head(self.download_url).headers.get("Content-Length", 0)))
            with ThreadPoolExecutor(max_workers=self.maximum_threads) as executor:
                futures = []
                start_pos = Decimal("0")
                while start_pos < content_length + int(content_length % self.chunk_size):
                    futures.append(
                        executor.submit(self.__download_chunk, self.download_url, start_pos,
                                        min(start_pos + self.chunk_size, content_length)))
                    start_pos += self.chunk_size
                
                for future in as_completed(futures):
                    queue.put(future.result())
        else:
            content = requests.get(self.download_url).content
            queue.put({"Start": 0, "End": len(content), "Content": content})
        with Path(self.download_file_path / self.download_file_name).open(mode="ab") as file:
            for i in range(queue.qsize()):
                response_data = queue.get()
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
            return {"Start": start_point, "End": end_point, "Content": response.content}
