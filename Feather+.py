import sys
import requests
import webbrowser
import random
import urllib.parse
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QListWidget, QStackedWidget, 
                             QProgressBar, QMessageBox, QSizeGrip, QSizePolicy, QDialog, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon, QMouseEvent, QImage, QPainter
from bs4 import BeautifulSoup
from io import BytesIO

class ImageDialog(QDialog):
    def __init__(self, image_url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Cover Art")
        self.setWindowFlags(Qt.Window | Qt.WindowFullscreenButtonHint)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title label with "Game Cover Art" text
        title_label = QLabel("Game Cover Art")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Box frame for the image
        self.box_frame = QFrame()
        self.box_frame.setStyleSheet("""
            QFrame {
                background-color: #111111;
                border: 2px solid #333333;
                border-radius: 5px;
            }
        """)
        self.box_frame.setMinimumSize(400, 400)
        
        # Image label inside the box
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Layout for the box frame
        box_layout = QVBoxLayout(self.box_frame)
        box_layout.addWidget(self.image_label)
        
        layout.addWidget(self.box_frame, alignment=Qt.AlignCenter)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                color: white;
                border: 1px solid #444444;
                padding: 5px 10px;
                min-width: 80px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        # Load the image
        self.load_image(image_url)

    def load_image(self, image_url):
        try:
            # Fix URLs that start with //
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            
            response = requests.get(image_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }, timeout=10)
            
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.read())
            
            if not pixmap.isNull():
                # Get screen dimensions
                screen = QApplication.primaryScreen()
                screen_size = screen.availableGeometry()
                
                # Calculate maximum size while maintaining aspect ratio
                max_width = screen_size.width() * 0.8  # 80% of screen width
                max_height = screen_size.height() * 0.7  # 70% of screen height
                
                # Scale the image to be as large as possible while fitting within screen
                scaled_pixmap = pixmap.scaled(
                    max_width, 
                    max_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Set the image
                self.image_label.setPixmap(scaled_pixmap)
                
                # Adjust dialog size to fit content
                self.adjustSize()
                
                # Center the dialog on screen
                self.move(
                    screen_size.center() - self.rect().center()
                )
                
                self.current_image_url = image_url
            else:
                self.show_error("Failed to load image")
        except Exception as e:
            self.show_error(f"Failed to fetch image: {str(e)}")

    def show_error(self, message):
        error_label = QLabel(message)
        error_label.setStyleSheet("color: white; font-size: 16px;")
        error_label.setAlignment(Qt.AlignCenter)
        self.box_frame.layout().addWidget(error_label)

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #000000; border-bottom: 1px solid #333333;")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)
        
        # Title label
        self.title = QLabel("Feather")
        self.title.setStyleSheet("color: #ffffff; font-size: 14px; padding-left: 5px;")
        self.title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Spacer
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Minimize button
        self.minimize_button = QPushButton("—")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        
        # Maximize/Restore button
        self.maximize_button = QPushButton("□")
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        
        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton:hover {
                background-color: #ff5555;
                color: #000000;
            }
        """)
        self.close_button.clicked.connect(self.parent.close)
        
        # Add widgets to layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.spacer)
        self.layout.addWidget(self.minimize_button)
        self.layout.addWidget(self.maximize_button)
        self.layout.addWidget(self.close_button)
        
        # Mouse position for dragging
        self.mouse_pos = None
    
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.mouse_pos and event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.mouse_pos)
            self.parent.move(self.parent.pos() + delta)
            self.mouse_pos = event.globalPos()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumSize(150, 40)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
                border: 1px solid #444444;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #555555;
            }
            QPushButton:pressed {
                background-color: #111111;
                border: 1px solid #333333;
            }
        """)

class GameDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feather")
        self.setGeometry(100, 100, 1000, 700)
        
        # Remove default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Add custom title bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Set app style
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #111111;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QListWidget {
                background-color: #111111;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #222222;
            }
            QListWidget::item:selected {
                background-color: #333333;
            }
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #111111;
            }
            QProgressBar::chunk {
                background-color: #555555;
                width: 10px;
            }
        """)
        
        # Header
        self.header = QLabel("Feather")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        self.header.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.header)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        # Add content widget to main layout
        self.main_layout.addWidget(self.content_widget)
        
        # Create pages
        self.create_loading_page()
        self.create_main_page()
        self.create_search_page()
        self.create_results_page()
        
        # Start with loading page
        self.stacked_widget.setCurrentIndex(0)
        
        # Game data
        self.combined_downloads = []
        self.current_games_list = []
        self.data_loaded = False
        self.current_selected_game = None
        self.current_image_url = None
        self.image_cache = {}
        
        # SteamGridDB API key
        self.steamgrid_api_key = "STEAMGRIDDAPI"
        
        # Load data after a short delay to show loading animation
        QTimer.singleShot(1500, self.load_data)
    
    def extract_clean_game_name(self, full_title):
        """Extract just the game name from complex titles"""
        # Remove everything after the first bracket or parenthesis
        clean_name = re.split(r'[\[\(\|]', full_title)[0].strip()
        return clean_name
    
    def create_loading_page(self):
        self.loading_page = QWidget()
        layout = QVBoxLayout(self.loading_page)
        layout.setAlignment(Qt.AlignCenter)
        
        # Loading animation
        self.loading_label = QLabel("Loading game data...")
        self.loading_label.setStyleSheet("color: #ffffff;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setFixedWidth(300)
        
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        
        self.stacked_widget.addWidget(self.loading_page)
    
    def create_main_page(self):
        self.main_page = QWidget()
        layout = QVBoxLayout(self.main_page)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Feather!")
        welcome_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
            padding-bottom: 10px;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label, alignment=Qt.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Your one-stop platform for game downloads")
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #aaaaaa;
            padding-bottom: 20px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        
        # Options label
        options_label = QLabel("Choose an option:")
        options_label.setStyleSheet("""
            font-size: 16px;
            color: #ffffff;
            padding: 15px 0;
        """)
        options_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(options_label, alignment=Qt.AlignCenter)
        
        # Buttons container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(30)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Show All Games button
        self.show_all_btn = AnimatedButton("Show All Games")
        self.show_all_btn.setIcon(QIcon.fromTheme("view-list-icons"))
        self.show_all_btn.setIconSize(QSize(20, 20))
        self.show_all_btn.clicked.connect(self.show_all_games)
        button_layout.addWidget(self.show_all_btn)
        
        # Search Games button
        self.search_btn = AnimatedButton("Search Games")
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.setIconSize(QSize(20, 20))
        self.search_btn.clicked.connect(self.show_search_page)
        button_layout.addWidget(self.search_btn)
        
        # Surprise Me button
        self.surprise_btn = AnimatedButton("Surprise Me!")
        self.surprise_btn.setIcon(QIcon.fromTheme("emblem-favorite"))
        self.surprise_btn.setIconSize(QSize(20, 20))
        self.surprise_btn.clicked.connect(self.surprise_me)
        button_layout.addWidget(self.surprise_btn)
        
        layout.addWidget(button_container, alignment=Qt.AlignCenter)
        
        # Add some vertical spacing at the bottom
        layout.addStretch(1)
        
        self.stacked_widget.addWidget(self.main_page)
    
    def create_search_page(self):
        self.search_page = QWidget()
        layout = QVBoxLayout(self.search_page)
        layout.setSpacing(20)
        
        # Back button
        back_btn = AnimatedButton("Back")
        back_btn.clicked.connect(self.show_main_page)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        
        # Search field
        search_label = QLabel("Search for a game:")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter game title...")
        self.search_input.returnPressed.connect(self.perform_search)
        layout.addWidget(self.search_input)
        
        # Search button
        self.search_submit_btn = AnimatedButton("Search")
        self.search_submit_btn.clicked.connect(self.perform_search)
        layout.addWidget(self.search_submit_btn, alignment=Qt.AlignCenter)
        
        self.stacked_widget.addWidget(self.search_page)
    
    def create_results_page(self):
        self.results_page = QWidget()
        layout = QHBoxLayout(self.results_page)
        layout.setSpacing(20)
        
        # Left side (game list)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Back button
        back_btn = AnimatedButton("Back")
        back_btn.clicked.connect(self.show_previous_page)
        left_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        
        # Results label
        self.results_label = QLabel()
        self.results_label.setStyleSheet("font-size: 18px; color: #ffffff;")
        self.results_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.results_label)
        
        # Games list
        self.games_list = QListWidget()
        self.games_list.itemClicked.connect(self.on_game_selected)
        left_layout.addWidget(self.games_list)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # Download button
        self.download_btn = AnimatedButton("Download")
        self.download_btn.clicked.connect(self.download_selected_game)
        button_layout.addWidget(self.download_btn)
        
        left_layout.addWidget(button_container)
        
        # Right side (image preview)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        
        # Image preview label
        image_label = QLabel("Game Cover Art")
        image_label.setStyleSheet("font-size: 16px; color: #ffffff;")
        image_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(image_label)
        
        # Image preview frame
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("background-color: #111111; border: 1px solid #333333;")
        self.image_frame.setFixedSize(400, 400)  # Larger preview area
        self.image_frame_layout = QVBoxLayout(self.image_frame)
        self.image_frame_layout.setAlignment(Qt.AlignCenter)
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("No image selected")
        self.image_preview.setStyleSheet("color: #aaaaaa;")
        self.image_preview.mousePressEvent = self.show_fullscreen_image
        self.image_frame_layout.addWidget(self.image_preview)
        
        right_layout.addWidget(self.image_frame)
        
        # Add some stretch to push everything up
        right_layout.addStretch()
        
        # Add left and right widgets to main layout
        layout.addWidget(left_widget, stretch=2)
        layout.addWidget(right_widget, stretch=1)
        
        self.stacked_widget.addWidget(self.results_page)
    
    def show_fullscreen_image(self, event):
        if hasattr(self, 'current_image_url') and self.current_image_url:
            image_dialog = ImageDialog(self.current_image_url, self)
            image_dialog.exec_()
    
    def load_data(self):
        if self.data_loaded:
            self.show_main_page()
            return
            
        urls_file = "urls.txt"
        
        try:
            with open(urls_file, 'r') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            self.show_error(f"File {urls_file} not found. Please ensure the file exists.")
            return
        
        self.combined_downloads = []
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    downloads = data.get("downloads", [])
                    self.combined_downloads.extend(downloads)
                else:
                    self.show_warning(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.show_warning(f"Error fetching data from {url}: {e}")
        
        self.data_loaded = True
        self.show_main_page()
    
    def show_all_games(self):
        if not self.combined_downloads:
            self.show_warning("No games available to display.")
            return
        
        self.current_games_list = self.combined_downloads
        self.display_games("All Available Games")
        self.previous_page = 1
        self.stacked_widget.setCurrentIndex(3)
    
    def show_search_page(self):
        self.previous_page = 1
        self.stacked_widget.setCurrentIndex(2)
    
    def show_main_page(self):
        self.stacked_widget.setCurrentIndex(1)
    
    def show_previous_page(self):
        if hasattr(self, 'previous_page'):
            self.stacked_widget.setCurrentIndex(self.previous_page)
        else:
            self.show_main_page()
    
    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            self.show_warning("Please enter a search term.")
            return
        
        search_results = []
        for game in self.combined_downloads:
            game_title = game.get("title", "")
            clean_title = self.extract_clean_game_name(game_title)
            if query.lower() in clean_title.lower():
                search_results.append(game)
        
        if not search_results:
            self.show_info("No games found with that search query.")
            return
        
        self.current_games_list = search_results
        self.display_games(f"Search Results for '{query}'")
        self.previous_page = 2
        self.stacked_widget.setCurrentIndex(3)
    
    def display_games(self, title):
        self.results_label.setText(title)
        self.games_list.clear()
        
        for game in self.current_games_list:
            title = game.get("title", "No Title")
            file_size = game.get("fileSize", "No Size")
            item_text = f"{title} | {file_size}"
            self.games_list.addItem(item_text)
    
    def on_game_selected(self, item):
        index = self.games_list.row(item)
        if 0 <= index < len(self.current_games_list):
            self.current_selected_game = self.current_games_list[index]
            self.show_game_image(self.current_selected_game.get("title", ""))
    
    def show_game_image(self, game_title):
        if not game_title:
            self.image_preview.setText("No game title available")
            return

        clean_title = self.extract_clean_game_name(game_title)
        self.image_preview.setText(f"Loading image for: {clean_title}")
        QApplication.processEvents()

        # Try to load from cache first
        if clean_title in self.image_cache:
            self.display_image_preview(self.image_cache[clean_title])
            return

        # Search SteamGridDB in background
        QTimer.singleShot(0, lambda: self.fetch_steamgrid_image(clean_title))
    
    def fetch_steamgrid_image(self, game_title):
        try:
            headers = {
                'Authorization': f'Bearer {self.steamgrid_api_key}',
                'User-Agent': 'Feather Game Downloader/1.0'
            }
            
            # First search for the game ID
            search_url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{urllib.parse.quote(game_title)}"
            search_response = requests.get(search_url, headers=headers, timeout=10)
            
            if search_response.status_code != 200:
                raise Exception(f"API returned status code {search_response.status_code}")
                
            search_data = search_response.json()
            
            if not search_data.get('success', False) or not search_data.get('data', []):
                raise Exception("No results found on SteamGridDB")
                
            # Get the first result's ID
            game_id = search_data['data'][0]['id']
            
            # Now get grids (cover art) for this game
            grids_url = f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}"
            grids_response = requests.get(grids_url, headers=headers, timeout=10)
            
            if grids_response.status_code != 200:
                raise Exception(f"API returned status code {grids_response.status_code}")
                
            grids_data = grids_response.json()
            
            if not grids_data.get('success', False) or not grids_data.get('data', []):
                raise Exception("No cover art found for this game")
                
            # Get the first image URL
            image_url = grids_data['data'][0]['url']
            
            # Download the image
            image_response = requests.get(image_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }, timeout=10)
            
            if image_response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(image_response.content)
                
                if not pixmap.isNull():
                    # Cache the image
                    self.image_cache[game_title] = pixmap
                    self.current_image_url = image_url
                    self.display_image_preview(pixmap)
                    return
            
            # If we get here, no image was found
            self.display_fallback_image()
            
        except Exception as e:
            print(f"Error loading image from SteamGridDB: {str(e)}")
            self.display_fallback_image()
    
    def display_fallback_image(self):
        # Create a simple fallback image
        pixmap = QPixmap(400, 400)
        pixmap.fill(Qt.darkGray)
        
        painter = QPainter(pixmap)
        painter.setPen(Qt.white)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "No Cover Art\nAvailable")
        painter.end()
        
        self.image_preview.setPixmap(pixmap)
        self.current_image_url = None
    
    def display_image_preview(self, pixmap):
        scaled_pixmap = pixmap.scaled(
            self.image_frame.width() - 20,
            self.image_frame.height() - 20,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_preview.setPixmap(scaled_pixmap)
    
    def download_selected_game(self):
        selected_items = self.games_list.selectedItems()
        if not selected_items:
            self.show_warning("Please select a game first.")
            return
        
        self.download_game(selected_items[0])
    
    def download_game(self, item):
        index = self.games_list.row(item)
        if 0 <= index < len(self.current_games_list):
            selected_game = self.current_games_list[index]
            magnet_link = selected_game.get("uris", [None])[0]
            
            if magnet_link:
                self.show_info(f"Opening magnet link for: {selected_game['title']}")
                webbrowser.open(magnet_link)
            else:
                self.show_error("No magnet link found for the selected game.")
    
    def surprise_me(self):
        if not self.combined_downloads:
            self.show_warning("No games available to select.")
            return
        
        # Select a random game
        random_game = random.choice(self.combined_downloads)
        magnet_link = random_game.get("uris", [None])[0]
        
        if not magnet_link:
            self.show_error("No magnet link found for the selected game.")
            return
        
        # Create confirmation dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Surprise Game!")
        msg.setText(f"Would you like to download:\n\n{random_game['title']}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        # Style the message box
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #000000;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #222222;
                color: white;
                border: 1px solid #444444;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        
        # Show the dialog and check the response
        response = msg.exec_()
        if response == QMessageBox.Yes:
            self.show_info(f"Opening magnet link for: {random_game['title']}")
            webbrowser.open(magnet_link)
    
    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #000000;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #222222;
                color: white;
                border: 1px solid #444444;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec_()
    
    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #000000;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #222222;
                color: white;
                border: 1px solid #444444;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec_()
    
    def show_info(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Information")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #000000;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #222222;
                color: white;
                border: 1px solid #444444;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set palette for dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(17, 17, 17))
    palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(34, 34, 34))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(85, 85, 85))
    palette.setColor(QPalette.Highlight, QColor(85, 85, 85))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    # Set application font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = GameDownloaderApp()
    window.show()
    sys.exit(app.exec_())
