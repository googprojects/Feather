import sys
import requests
import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QPushButton

class GameDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feather")
        self.setGeometry(100, 100, 1500, 900)
        self.setStyleSheet("background-color: #121212; color: white;")
        
        self.layout = QVBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search for a game...")
        self.search_bar.setStyleSheet("background-color: #333; color: white; padding: 5px;")
        self.search_bar.returnPressed.connect(self.search_game)
        
        self.game_list = QListWidget(self)
        self.game_list.setStyleSheet("background-color: #222; color: white;")
        self.game_list.itemDoubleClicked.connect(self.open_magnet_link)
        
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.game_list)
        self.setLayout(self.layout)
        
        self.urls_file = "urls.txt"
        self.combined_downloads = []
        self.load_games()
    
    def load_games(self):
        urls = []
        try:
            with open(self.urls_file, 'r') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            print(f"File {self.urls_file} not found. Please ensure the file exists.")
            return
        
        for url in urls:
            data = self.fetch_data_from_url(url)
            if data:
                downloads = data.get("downloads", [])
                self.combined_downloads.extend(downloads)
        
        self.display_games(self.combined_downloads)
    
    def fetch_data_from_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
        return None
    
    def display_games(self, games_list):
        self.game_list.clear()
        for game in games_list:
            title = game.get("title", "No Title")
            file_size = game.get("fileSize", "No Size")
            item_text = f"{title} | {file_size}"
            self.game_list.addItem(item_text)

    
    def search_game(self):
        query = self.search_bar.text().strip().lower()
        filtered_games = [game for game in self.combined_downloads if query in game.get("title", "").lower()]
        self.display_games(filtered_games)
    
    def open_magnet_link(self, item):
        selected_title = item.text()
        for game in self.combined_downloads:
            if game.get("title") == selected_title:
                magnet_link = game.get("uris", [None])[0]
                if magnet_link:
                    print(f"Opening magnet link for: {selected_title}")
                    webbrowser.open(magnet_link)
                else:
                    print("No magnet link found for the selected game.")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameDownloader()
    window.show()
    sys.exit(app.exec_())
