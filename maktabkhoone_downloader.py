import sys
import os
import argparse
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QProgressDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maktabkhoone Video Downloader")
        self.setGeometry(100, 100, 600, 400)
        self.default_download_path = os.path.expanduser("~")

        self.initUI()

    def initUI(self):
        logo_label = QLabel(self)
        pixmap = QPixmap("logo.svg")
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        url_label = QLabel("URL:", self)
        self.url_input = QLineEdit(self)

        username_label = QLabel("Username:", self)
        self.username_input = QLineEdit(self)

        password_label = QLabel("Password:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.download_path_label = QLabel("Download Path:", self)
        self.download_path_input = QLineEdit(self)
        self.download_path_input.setText(self.default_download_path) 
        self.download_path_input.setReadOnly(True)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse)

        download_button = QPushButton("Download", self)
        download_button.clicked.connect(self.download)

        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.download_path_label)
        layout.addWidget(self.download_path_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(download_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def browse(self):
        download_path = QFileDialog.getExistingDirectory(self, "Select Download Path", self.default_download_path)
        if download_path:
            self.download_path_input.setText(download_path)  

    def download(self):

        # self.progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 100, self)
        # self.progress_dialog.setWindowModality(Qt.WindowModal)
        # self.progress_dialog.setWindowTitle("Downloading")
        # self.progress_dialog.setAutoClose(True)
        # self.progress_dialog.show()
    
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)  
        driver.get(self.url_input.text())

        WebDriverWait(driver, 15).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "login"))
        )

        driver.find_element(By.ID,"login").click()

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "tessera"))
        )

        driver.find_element(By.ID,"tessera").send_keys(self.username_input.text())
        driver.find_element(By.CSS_SELECTOR,"button[data-tag='ga-email-phone-login']").click()

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )

        driver.find_element(By.ID,"password").send_keys(self.password_input.text())
        driver.find_element(By.CSS_SELECTOR,"button[data-tag='ga-password-submit']").click()

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "base-chapter__section"))
        )

        episodesATag = driver.find_element(By.CLASS_NAME,"base-chapter__section").find_elements(By.TAG_NAME,"a")

        episodesUrl = []

        for episode in episodesATag:
            href = episode.get_attribute("href")
            if href:
                episodesUrl.append(href)

        for episodeUrl in episodesUrl:

            print("Episode URL:", episodeUrl)

            driver.get(episodeUrl)

            WebDriverWait(driver, 15).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

            video_source = driver.find_element(By.CSS_SELECTOR, "meta[property='og:video']").get_attribute("content")

            print("Video Source:", video_source)

            self.download_video(video_source)

        # self.progress_dialog.hide()
        # driver.quit()

    def download_video(self, video_url):
        print("video_url : ",video_url)
        download_path = os.path.join(self.download_path_input.text(), "videos")
        os.makedirs(download_path, exist_ok=True)

        filename = os.path.basename(video_url)

        response = requests.get(video_url)
        if response.status_code == 200:
            with open(os.path.join(download_path, filename), 'wb') as f:
                f.write(response.content)
                print("Video downloaded successfully.")
        else:
            print("Failed to download video.")

    def update_progress(self, value):
        self.progress_dialog.setValue(value)

    def download_finished(self):
        self.progress_dialog.close()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Maktabkhoone Video Downloader")
    parser.add_argument("--url", help="URL of the website to download from", type=str)
    parser.add_argument("--output", help="Output directory for downloaded videos", type=str)
    return parser.parse_args()


def run_gui():
    app = QApplication(sys.argv)
    window = VideoDownloaderGUI()
    window.show()
    sys.exit(app.exec_())


def run_cli(args):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)  
    driver.get(args.url) 

    episodes = driver.find_elements(By.TAG_NAME, "li")

    for episode in episodes:
        episode_url = episode.find_element(By.TAG_NAME, "a").get_attribute("href")
        print("Episode URL:", episode_url)

        driver.get(episode_url)

        video_element = driver.find_element(By.TAG_NAME, "video")

        video_source = video_element.get_attribute("src")
        print("Video Source:", video_source)

        download_video(video_source, args.output)

    driver.quit()


def download_video(video_url, output_dir):
    download_path = os.path.join(output_dir, "videos")
    os.makedirs(download_path, exist_ok=True)

    filename = os.path.basename(video_url)

    response = requests.get(video_url)
    if response.status_code == 200:
        with open(os.path.join(download_path, filename), 'wb') as f:
            f.write(response.content)
            print("Video downloaded successfully.")
    else:
        print("Failed to download video.")


if __name__ == "__main__":
    args = parse_arguments()
    if args.url:
        run_cli(args)
    else:
        run_gui()
