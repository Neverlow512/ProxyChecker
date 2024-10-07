import sys
import json
import csv
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPlainTextEdit, QPushButton, QComboBox, QProgressBar, 
                             QMessageBox)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import requests
import time
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QSize

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller. """
    if getattr(sys, 'frozen', False):  # If the app is compiled
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon_path = get_resource_path('ProxyChecker.jpg')
twitter_svg_path = get_resource_path('twitter.svg')  # Path to Twitter icon
reddit_svg_path = get_resource_path('reddit.svg')    # Path to Reddit icon

def get_app_dir():
    if getattr(sys, 'frozen', False):
        # If the application is frozen (compiled)
        if sys.platform == 'darwin':
            # macOS app bundle (.app)
            bundle_dir = os.path.dirname(os.path.abspath(sys.executable))
            # The .app structure is /path/to/YourApp.app/Contents/MacOS/YourAppExecutable
            # So we need to go up three levels to get to the directory where the .app resides
            return os.path.abspath(os.path.join(bundle_dir, '..', '..', '..'))
        else:
            # For Windows and Linux
            return os.path.dirname(sys.executable)
    else:
        # Not frozen: running as a script
        return os.path.dirname(os.path.abspath(__file__))

# Define application-specific files
APP_DIR = get_app_dir()
CONFIG_PATH = os.path.join(APP_DIR, 'config.json')
RESULTS_PATH = os.path.join(APP_DIR, 'proxy_results.csv')

class ProxyCheckerThread(QThread):
    update_log = pyqtSignal(str)
    update_progress = pyqtSignal(int)

    def __init__(self, api_key, proxies, proxy_type, max_score):
        super().__init__()
        self.api_key = api_key
        self.proxies = proxies
        self.proxy_type = proxy_type
        self.max_score = max_score
        self.results = []

    def run(self):
        total_proxies = len(self.proxies)
        for i, proxy in enumerate(self.proxies):
            result = self.check_proxy(proxy)
            if result["Score"] <= self.max_score:
                self.results.append(result)
            self.update_progress.emit(int((i + 1) / total_proxies * 100))
            time.sleep(1)  # Add a small delay between requests
        self.save_results()

    def check_proxy(self, proxy):
        # Parse the proxy string
        parts = proxy.split(':')
        if len(parts) == 4:
            ip, port, user, password = parts
        elif len(parts) == 2:
            ip, port = parts
            user = password = None
        else:
            self.update_log.emit(f"Invalid proxy format: {proxy}")
            return self.get_error_result(proxy)

        # Build the proxy URL
        if self.proxy_type == "HTTP":
            scheme = "http"
        elif self.proxy_type == "SOCKS5":
            scheme = "socks5"
        else:
            self.update_log.emit(f"Unsupported proxy type: {self.proxy_type}")
            return self.get_error_result(proxy)
        if user and password:
            proxy_url = f"{scheme}://{user}:{password}@{ip}:{port}"
        else:
            proxy_url = f"{scheme}://{ip}:{port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        try:
            self.update_log.emit(f"Testing proxy: {proxy}")
            # Make a request via the proxy to get external IP
            response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
            response.raise_for_status()
            external_ip = response.json().get("ip", "")
            self.update_log.emit(f"Proxy {proxy} is working. External IP: {external_ip}")

            # Now, call IPQualityScore API on external_ip
            api_url = f"https://ipqualityscore.com/api/json/ip/{self.api_key}/{external_ip}"
            api_params = {
                "strictness": 1,
                "allow_public_access_points": "true",
                "fast": "true",
                "lighter_penalties": "true",
            }
            api_response = requests.get(api_url, params=api_params, timeout=10)
            api_data = api_response.json()
            if api_data.get("success", False):
                result = {
                    "Proxy": proxy,
                    "Score": api_data.get("fraud_score", 0),
                    "City": api_data.get("city", "Unknown"),
                    "Country": api_data.get("country_code", "Unknown"),
                    "ISP": api_data.get("ISP", "Unknown"),
                    "Latitude": api_data.get("latitude", "Unknown"),
                    "Longitude": api_data.get("longitude", "Unknown")
                }
                self.update_log.emit(f"Successfully checked proxy {proxy}. Fraud Score: {result['Score']}")
                return result
            else:
                self.update_log.emit(f"Failed to get data from IPQualityScore for IP {external_ip}. API response: {api_data}")
                return self.get_error_result(proxy)
        except requests.RequestException as e:
            self.update_log.emit(f"Network error testing proxy {proxy}: {str(e)}")
            return self.get_error_result(proxy)
        except Exception as e:
            self.update_log.emit(f"Unexpected error testing proxy {proxy}: {str(e)}")
            return self.get_error_result(proxy)

    def get_error_result(self, proxy):
        return {
            "Proxy": proxy,
            "Score": 100,
            "City": "Unknown",
            "Country": "Unknown",
            "ISP": "Unknown",
            "Latitude": "Unknown",
            "Longitude": "Unknown"
        }

    def save_results(self):
        # Save self.results to CSV
        fieldnames = ["Proxy", "Score", "City", "Country", "ISP", "Latitude", "Longitude"]
        try:
            with open(RESULTS_PATH, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
            self.update_log.emit(f"Results saved to {RESULTS_PATH}")
        except Exception as e:
            self.update_log.emit(f"Error saving results: {str(e)}")

class ProxyCheckerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proxy Checker")
        self.setGeometry(100, 100, 600, 400)
        self.setup_ui()
        self.load_api_key()
        QTimer.singleShot(0, self.set_dark_theme)

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        social_media_layout = QHBoxLayout()

        # Twitter SVG icon
        twitter_svg_icon = QSvgWidget(twitter_svg_path)  # Adjust path as necessary
        twitter_svg_icon.setFixedSize(QSize(24, 24))  # Set the fixed size for the SVG icon
        twitter_svg_icon.mousePressEvent = lambda event: self.open_link("https://x.com/traffic_goat")

        twitter_label = QLabel('<a href="https://x.com/traffic_goat">traffic_goat</a>')
        twitter_label.setOpenExternalLinks(True)
        twitter_label.setStyleSheet("""
            QLabel { 
                color: #FF4500;  /* Bright orange for visibility */
                font-weight: bold; 
                font-size: 13px; 
                text-decoration: none;  /* No underline */
            }
            QLabel:hover { 
                color: #FFD700;  /* Change to gold on hover */
                text-decoration: underline;  /* Underline on hover */
            }
        """)

        social_media_layout.addWidget(twitter_svg_icon)
        social_media_layout.addWidget(twitter_label)

        # Reddit SVG icon
        reddit_svg_icon = QSvgWidget(reddit_svg_path)  # Adjust path as necessary
        reddit_svg_icon.setFixedSize(QSize(24, 24))  # Set the fixed size for the SVG icon
        reddit_svg_icon.mousePressEvent = lambda event: self.open_link("https://www.reddit.com/user/Neverlow512/")

        reddit_label = QLabel('<a href="https://www.reddit.com/user/Neverlow512/">Neverlow512</a>')
        reddit_label.setOpenExternalLinks(True)
        reddit_label.setStyleSheet("""
            QLabel { 
                color: #FF4500;  /* Bright orange for visibility */
                font-weight: bold; 
                font-size: 13px; 
                text-decoration: none;  /* No underline */
            }
            QLabel:hover { 
                color: #FFD700;  /* Change to gold on hover */
                text-decoration: underline;  /* Underline on hover */
            }
        """)

        social_media_layout.addWidget(reddit_svg_icon)
        social_media_layout.addWidget(reddit_label)

        layout.addLayout(social_media_layout)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        self.api_key_input = QPlainTextEdit()
        self.api_key_input.setFixedHeight(30)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Proxy Type
        proxy_type_layout = QHBoxLayout()
        proxy_type_label = QLabel("Proxy Type:")
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "SOCKS5"])
        self.proxy_type_combo.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #2b2b2b;
                border: 1px solid #555;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #555;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
            }
            QComboBox QAbstractItemView {
                color: white;
                background-color: #2b2b2b;
                border: 1px solid #555;
                selection-background-color: #3a3a3a;
            }
        """)

        proxy_type_layout.addWidget(proxy_type_label)
        proxy_type_layout.addWidget(self.proxy_type_combo)
        layout.addLayout(proxy_type_layout)

        # Max Score
        max_score_layout = QHBoxLayout()
        max_score_label = QLabel("Max Score:")
        self.max_score_input = QPlainTextEdit()
        self.max_score_input.setFixedHeight(30)
        max_score_layout.addWidget(max_score_label)
        max_score_layout.addWidget(self.max_score_input)
        layout.addLayout(max_score_layout)

        # Proxies Input
        proxies_label = QLabel("Enter proxies (one per line):")
        layout.addWidget(proxies_label)
        self.proxies_input = QPlainTextEdit()
        layout.addWidget(self.proxies_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Check Proxies")
        self.check_button.clicked.connect(self.start_checking)
        button_layout.addWidget(self.check_button)
        layout.addLayout(button_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Log Display
        log_label = QLabel("Log:")
        layout.addWidget(log_label)
        self.log_display = QPlainTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

    def open_link(self, url):
        QDesktopServices.openUrl(QUrl(url))

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)

        self.check_button.setStyleSheet("QPushButton { background-color: #FF4500; color: white; }")
        self.progress_bar.setStyleSheet("QProgressBar { background-color: #2b2b2b; border: 1px solid #2b2b2b; }"
                                        "QProgressBar::chunk { background-color: #FF4500; }")
        self.proxy_type_combo.setStyleSheet("QComboBox { color: black; }")

    def load_api_key(self):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                self.api_key_input.setPlainText(config.get('api_key', ''))
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            self.show_error("Error loading API key", "The config file is corrupted. Please re-enter your API key.")
        self.api_key_input.textChanged.connect(self.save_api_key)

    def save_api_key(self):
        api_key = self.api_key_input.toPlainText().strip()
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump({'api_key': api_key}, f)
        except Exception as e:
            self.show_error("Error saving API key", f"Failed to save API key: {str(e)}")

    def start_checking(self):
        api_key = self.api_key_input.toPlainText().strip()
        if not api_key:
            self.show_error("API Key Missing", "Please enter your API key.")
            return

        proxy_type = self.proxy_type_combo.currentText()
        
        try:
            max_score = float(self.max_score_input.toPlainText())
            if not (0 <= max_score <= 100):
                raise ValueError("Score must be between 0 and 100")
        except ValueError:
            self.show_error("Invalid Max Score", "Please enter a valid number between 0 and 100 for the max score.")
            return

        proxies = [proxy.strip() for proxy in self.proxies_input.toPlainText().split('\n') if proxy.strip()]
        if not proxies:
            self.show_error("No Proxies", "Please enter at least one proxy.")
            return

        self.thread = ProxyCheckerThread(api_key, proxies, proxy_type, max_score)
        self.thread.update_log.connect(self.update_log)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.checking_finished)
        self.thread.start()

        self.check_button.setEnabled(False)

    def update_log(self, message):
        self.log_display.appendPlainText(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def checking_finished(self):
        self.check_button.setEnabled(True)
        self.update_log("Proxy checking completed.")

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProxyCheckerGUI()
    window.show()
    sys.exit(app.exec())
