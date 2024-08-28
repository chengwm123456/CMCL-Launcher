# -*- coding: utf-8 -*-
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path
from queue import Queue


class Downloader:
    def __init__(self, download_url, download_file_name, download_file_path="", maximum_threads=64):
        self.download_url = download_url
        self.download_file_name = Path(download_file_name)
        self.download_file_path = Path(download_file_path)
        self.maximum_threads = maximum_threads
    
    def download(self, maximum_threads=None):
        if maximum_threads is not None:
            self.maximum_threads = maximum_threads
        content_length = Decimal(requests.head(self.download_url).headers.get("Content-Length"))
        
        queue = Queue()
        with ThreadPoolExecutor(max_workers=self.maximum_threads) as executor:
            futures = []
            current_thread_num = threading.active_count() - 1
            chunk_size = current_thread_num
            for i in range(current_thread_num):
                start_point = i * chunk_size
                end_point = start_point + chunk_size - 1 if i < current_thread_num - 1 else content_length - 1
                futures.append(
                    executor.submit(self.__download_chunk, self.download_url, start_point, end_point))
            
            for future in as_completed(futures):
                queue.put(future.result())
        
        with Path(self.download_file_path / self.download_file_name).open(mode="ab") as file:
            for i in range(queue.qsize()):
                response_data = queue.get()
                file.seek(response_data["Start"])
                file.write(response_data["Content"])
    
    @staticmethod
    def __download_chunk(download_url, start_point, end_point):
        headers = {"Range": f"bytes={start_point}-{end_point}"}
        response = requests.get(download_url, headers=headers, stream=True, verify=True)
        if response.status_code == 206:
            return {"Start": start_point, "End": end_point, "Content": response.content}
