import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QProgressBar, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from downloader import DownloadThread
from utils import is_valid_youtube_url

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Youtube to MP3")
        self.setGeometry(100, 100, 600, 200)
        
        self.layout = QVBoxLayout()  # Użyj self.layout
        
        self.label = QLabel("YouTube Link:")
        self.label.setAlignment(Qt.AlignCenter)  # Wyśrodkowanie tekstu
        self.layout.addWidget(self.label)
        
        self.url_input = QLineEdit()
        self.url_input.textChanged.connect(self.validate_url)
        self.layout.addWidget(self.url_input)
        
        self.download_button = QPushButton("Download MP3")
        self.download_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.download_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)  # Ustawienie wartości na 0%
        self.progress_bar.setFormat("0%")  # Ustawienie tekstu domyślnego na 0%
        self.layout.addWidget(self.progress_bar)
        
        self.checkmark_label = QLabel("")  # Deklaracja nowej etykiety
        self.checkmark_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.checkmark_label)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def resizeEvent(self, event):
        self.progress_bar.setMaximumWidth(self.width())
        QMainWindow.resizeEvent(self, event)

    def validate_url(self):
        url = self.url_input.text()
        if not url:
            self.url_input.setStyleSheet("border: 2px solid red;")
        elif is_valid_youtube_url(url):
            self.url_input.setStyleSheet("border: 2px solid green;")
        else:
            self.url_input.setStyleSheet("border: 2px solid red;")

    def is_valid_youtube_url(self, url):
        return "youtube.com" in url or "youtu.be" in url

    def start_download(self):
        url = self.url_input.text()
        if not is_valid_youtube_url(url):
            self.url_input.setStyleSheet("border: 2px solid red;")
            QTimer.singleShot(1000, lambda: self.url_input.setStyleSheet(""))  # Usunięcie podświetlenia po 1 sekundzie
            return

        save_path = os.path.expanduser("~/Desktop")
        unique_save_path = self.generate_unique_filepath(save_path, '%(title)s (AV).%(ext)s')
        self.thread = DownloadThread(url, unique_save_path)
        self.thread.progress_changed.connect(self.update_progress)
        self.thread.download_complete.connect(self.download_complete)
        self.thread.download_failed.connect(self.download_failed)
        self.thread.start()

    def generate_unique_filepath(self, save_path, filename_template):
        base_path = os.path.join(save_path, filename_template % {"title": "%(title)s", "ext": "mp3"})
        counter = 1
        while os.path.exists(base_path % {"title": f"%(title)s ({counter})", "ext": "mp3"}):
            counter += 1
        return base_path % {"title": f"%(title)s ({counter})", "ext": "mp3"} if counter > 1 else base_path

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")  # Aktualizacja formatu

    def download_complete(self, filename):
        self.url_input.setStyleSheet("")  # Usunięcie podświetlenia
        self.progress_bar.setValue(100)  # Ustawienie na 100% po zakończeniu
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")  # Zmiana koloru paska postępu na zielony
        self.progress_bar.setFormat("")  # Usunięcie formatu wewnętrznego paska
        self.checkmark_label.setText("100% " + u'\u2713')  # Ustawienie wartości 100% i symbolu ptaszka na zewnątrz
        QTimer.singleShot(1000, self.reset_progress_bar)  # Usunięcie podświetlenia po 1 sekundzie
        self.url_input.clear()

    def reset_progress_bar(self):
       self.progress_bar.reset()
       self.progress_bar.setValue(0)  # Przywrócenie wartości na 0
       self.progress_bar.setFormat("0%")  # Przywrócenie 0%
       self.progress_bar.setStyleSheet("")  # Przywrócenie domyślnego koloru paska postępu
       self.checkmark_label.setText("")  # Usunięcie symbolu ptaszka

    def download_failed(self, error):
        self.url_input.setStyleSheet("border: 2px solid red;")
        QTimer.singleShot(1000, lambda: self.url_input.setStyleSheet(""))  # Usunięcie podświetlenia po 1 sekundzie
        QMessageBox.critical(self, "Błąd pobierania!", f"Podczas pobierania wystąpił błąd: {error}")
        self.progress_bar.setValue(0)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
