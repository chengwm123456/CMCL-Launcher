# -*- coding: utf-8 -*-
from .GetFabric import GetDownloadUrlBase
from ..CMCLCore.CMCLDefines.Downloader import Downloader


def DownloadFabric(game, loader, path, target_path):
    base_url = GetDownloadUrlBase(game, loader)
    base_url += "/" + path.strip("/")
    downloader = Downloader(base_url, "", target_path)
    downloader.downloadFile()


def DownloadFabricZip(game, loader, target_path):
    DownloadFabric(game, loader, "/profile/zip", target_path)
