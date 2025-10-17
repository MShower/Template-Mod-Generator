import shutil
import zipfile
from os import remove

import requests as rq
import zipfile as zf
import os

from textual.widgets import ProgressBar


def download_file(url: str,
                  dest: str,
                  ):
    try:
        #https://github.com/Fallen-Breath/fabric-mod-template/archive/refs/heads/master.zip
        response = rq.get(url, stream=True)
        total = int(response.headers.get("content-length", 0))
        if os.path.exists(dest):
            os.remove(dest)
        with open(dest, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return 1
    except:
        return 0


def unzip(file_name: str, force_unzip: bool = False):
    folder_name, ext = os.path.splitext(file_name)
    zip_file = zf.ZipFile(file_name)
    if os.path.isdir(folder_name):
        if force_unzip:
            shutil.rmtree(folder_name)
        else:
            return FileExistsError(folder_name)
    os.mkdir(folder_name)
    for names in zip_file.namelist():
        zip_file.extract(names, folder_name)
    zip_file.close()
    os.remove(file_name)
    return None


def pack(output: str, folder_path: str):
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
