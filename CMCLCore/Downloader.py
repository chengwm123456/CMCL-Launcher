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
    def __init__(self, download_url: str, download_file_name: Union[str, Path, PurePath, os.PathLike, LiteralString],
                 download_file_path: Union[str, Path, PurePath, os.PathLike, LiteralString] = ".",
                 maximum_threads: Union[int, str] = 64):
        self.download_url = download_url
        self.download_file_name = Path(download_file_name)
        self.download_file_path = Path(download_file_path)
        self.maximum_threads = int(maximum_threads)
    
    def download(self, maximum_threads: Optional[Union[int, str]] = None):
        if maximum_threads is not None:
            self.maximum_threads = int(maximum_threads)
        queue = Queue()
        range_request_state = requests.head(self.download_url).headers.get("Accept-Range", "none").lower()
        if range_request_state != "none":
            content_length = Decimal(requests.head(self.download_url).headers.get("Content-Length", 0))
            with ThreadPoolExecutor(max_workers=self.maximum_threads) as executor:
                futures = []
                current_thread_num = Decimal(threading.active_count() - 1)
                chunk_size = Decimal(current_thread_num)
                for i in range(int(current_thread_num)):
                    start_point = Decimal(i * chunk_size)
                    end_point = Decimal(
                        start_point + chunk_size - 1 if i < current_thread_num - 1 else content_length - 1)
                    futures.append(
                        executor.submit(self.__download_chunk, self.download_url, start_point, end_point))
                
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
    def __download_chunk(download_url: str, start_point: Union[int, float, Decimal],
                         end_point: Union[int, float, Decimal]):
        headers = {"Range": f"bytes={int(start_point)}-{int(end_point)}"}
        response = requests.get(download_url, headers=headers, stream=True, verify=True)
        if response.status_code == 206:
            return {"Start": start_point, "End": end_point, "Content": response.content}
