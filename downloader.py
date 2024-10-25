import os
import re
import yt_dlp as youtube_dl
from PyQt5.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    progress_changed = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    download_failed = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': self.save_path,
            'progress_hooks': [self.yt_progress_hook],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception as e:
            self.download_failed.emit(str(e))

    def yt_progress_hook(self, d):
        if d['status'] == 'downloading':
            percentage_str = d['_percent_str'].strip()
            percentage = float(re.sub(r'[^\d.]', '', percentage_str))  # Usuwamy niepotrzebne znaki
            self.progress_changed.emit(percentage)
        elif d['status'] == 'finished':
            filename = d['filename']
            new_filename = self.clean_filename(filename)
            if filename != new_filename:
                os.rename(filename, new_filename)
            self.download_complete.emit(new_filename)

    def clean_filename(self, filename):
        patterns = [r"\(Official Video\)", r"\(Official Music Video\)"]
        for pattern in patterns:
            filename = re.sub(pattern, "", filename, flags=re.IGNORECASE).strip()
        return filename
