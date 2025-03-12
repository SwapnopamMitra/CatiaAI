
import json
import os
import pathlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFileDialog, QInputDialog,
    QListWidget, QListWidgetItem, QSplitter, QHBoxLayout, QToolButton, QComboBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from config import Config


class CatiaBrowser(QMainWindow):
    CONFIG_FILE = os.path.join(Config.BASE_DIR, "browser", "browser_config.json")
    BOOKMARKS_FILE = os.path.join(Config.BASE_DIR, "browser", "bookmarks.json")
    HISTORY_FILE = os.path.join(Config.BASE_DIR, "browser", "history.json")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Catia Browser")
        self.setGeometry(200, 200, 1024, 768)

        # ✅ Load configuration (Theme + Wallpaper)
        self.current_theme = "dark"
        self.current_wallpaper = "default.jpg"
        self.load_config()

        # ✅ Initialize the browser engine
        self.browser = QWebEngineView()
        self.browser.urlChanged.connect(lambda url: self.save_history(url))

        # ✅ Create Bookmarks and History ListWidgets FIRST (fixes the error)
        self.bookmarks_list = QListWidget()
        self.history_list = QListWidget()

        # ✅ Connect them AFTER initializing
        self.bookmarks_list.itemClicked.connect(self.open_bookmark)
        self.history_list.itemClicked.connect(self.open_history_item)

        # ✅ URL Bar
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Search or enter URL...")
        self.url_bar.returnPressed.connect(self.load_url)

        # ✅ Theme Selector Dropdown
        self.theme_selector = QComboBox(self)
        self.theme_selector.addItems(["dark", "light", "cyberpunk", "blade_runner", "neon", "edgerunners", "gothic"])
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentIndexChanged.connect(self.change_theme)

        # ✅ Toolbar Buttons
        self.back_button = self.create_button("⏪", "Back", self.browser.back)
        self.forward_button = self.create_button("⏩", "Forward", self.browser.forward)
        self.reload_button = self.create_button("⟳", "Reload", self.browser.reload)
        self.bookmark_button = self.create_button("🔖", "Add Bookmark", self.add_bookmark)
        self.resize_button = self.create_button("🔲", "Resize Browser", self.resize_browser)
        self.change_wallpaper_button = self.create_button("🖼", "Change Wallpaper", self.change_wallpaper)

        # ✅ Split View Layout
        self.splitter = QSplitter()
        self.splitter.addWidget(self.bookmarks_list)
        self.splitter.addWidget(self.browser)
        self.splitter.setSizes([200, 800])

        # ✅ Load Bookmarks & History
        self.load_bookmarks()
        self.load_history()

        # ✅ Toolbar Layout
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.back_button)
        toolbar_layout.addWidget(self.forward_button)
        toolbar_layout.addWidget(self.reload_button)
        toolbar_layout.addWidget(self.bookmark_button)
        toolbar_layout.addWidget(self.resize_button)
        toolbar_layout.addWidget(self.change_wallpaper_button)
        toolbar_layout.addWidget(self.theme_selector)

        #PUPU
        self.history_button = self.create_button("📜", "Open History", lambda: self.history_list.show())
        self.bookmarks_button = self.create_button("📚", "Open Bookmarks", lambda: self.bookmarks_list.show())
        self.clear_history_button = self.create_button("🗑️", "Clear History", self.clear_history)
        self.clear_bookmarks_button = self.create_button("❌", "Clear Bookmarks", self.clear_bookmarks)
        self.downloads_button = self.create_button("📥", "Open Downloads", self.open_downloads)
        self.home_button = self.create_button("🏠", "Home", self.go_home)
        self.stop_button = self.create_button("⏹️", "Stop Loading", self.stop_loading)

        # Add new buttons to toolbar layout
        toolbar_layout.addWidget(self.history_button)
        toolbar_layout.addWidget(self.bookmarks_button)
        toolbar_layout.addWidget(self.clear_history_button)
        toolbar_layout.addWidget(self.clear_bookmarks_button)
        toolbar_layout.addWidget(self.downloads_button)
        toolbar_layout.addWidget(self.home_button)
        toolbar_layout.addWidget(self.stop_button)
        #PUPU

        #  Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.url_bar)
        main_layout.addWidget(self.splitter)

        #  Set Central Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load last opened URL (if any)
        if os.path.exists(self.CONFIG_FILE):
            self.browser.setUrl(QUrl.fromLocalFile(os.path.join(Config.BASE_DIR, "browser", "dashboard.html")))


        #Apply last theme and wallpaper
        self.apply_wallpaper(self.current_wallpaper)
        self.apply_theme(self.current_theme)


    #Inject CSS
    def inject_css(self, css):
        script = f"""
        var style = document.createElement('style');
        style.innerHTML = `{css}`;
        document.head.appendChild(style);
        """
        self.browser.page().runJavaScript(script)

    #Save Configuration
    def save_config(self, key, value):
        with open(self.CONFIG_FILE, "w") as file:
            json.dump({key: value}, file)

    #Load Configuration
    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as file:
                data = json.load(file)
            self.current_theme = data.get("theme", "dark")
            self.current_wallpaper = data.get("wallpaper", "")



    def change_wallpaper(self):
        file_dialog = QFileDialog()
        wallpaper_path, _ = file_dialog.getOpenFileName(self, "Choose Wallpaper", "", "Images (*.png *.jpg *.jpeg)")
        if wallpaper_path:
            wallpaper_url = QUrl.fromLocalFile(wallpaper_path).toString()
            self.apply_wallpaper(wallpaper_url)
            self.save_config("wallpaper", wallpaper_url)


    def apply_wallpaper(self, wallpaper_url):
        #Update dashboard.html with the new wallpaper
        dashboard_path = os.path.join(Config.BASE_DIR, "browser", "dashboard.html")
        
        with open(dashboard_path, "r") as file:
            content = file.read()

        # Dynamically update the background image without relying on "default.jpg"
        if 'background-image:' in content:
            start = content.index('background-image:')
            end = content.index(';', start)
            content = content[:start] + f'background-image: url("{wallpaper_url}")' + content[end:]

        with open(dashboard_path, "w") as file:
            file.write(content)

        # Reload the dashboard instantly
        self.browser.reload()

        # Function to record browsing history
    def save_history(self, url):
        url = url.toString()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.HISTORY_FILE, "a") as file:
            file.write(f"{timestamp} - {url}\n")
        self.load_history()

        # Function to add a bookmark
    def add_bookmark(self):
        url = self.browser.url().toString()
        name, ok = QInputDialog.getText(self, "Add Bookmark", "Enter a name for this bookmark:")
        if ok and name:
            with open(self.BOOKMARKS_FILE, "r+") as file:
                data = json.load(file)
                data[name] = url
                file.seek(0)
                json.dump(data, file, indent=4)
            self.load_bookmarks()
        # Load bookmarks from bookmarks.json

    def load_bookmarks(self):
        if not os.path.exists(self.BOOKMARKS_FILE):
            with open(self.BOOKMARKS_FILE, "w") as file:
                json.dump({}, file)
        with open(self.BOOKMARKS_FILE, "r") as file:
            data = json.load(file)
        self.bookmarks_list.clear()
        for name, url in data.items():
            item = QListWidgetItem(f"{name} - {url}")
            self.bookmarks_list.addItem(item)
        
        # Open a bookmark
    def open_bookmark(self, item):
        url = item.text().split(" - ")[-1]
        self.browser.setUrl(QUrl(url))

        # Open history item
    def open_history_item(self, item):
        url = item.text().split(" - ")[-1]
        self.browser.setUrl(QUrl(url))



    def on_theme_change(self):
        new_theme = self.theme_selector.currentText()
        self.apply_theme(new_theme)
        self.save_config("theme", new_theme)

        # Load URL from the URL bar
    def load_url(self):
        url = self.url_bar.text().strip()
        if not url:
            # If no URL is entered, go to home page
            dashboard_path = os.path.join(Config.BASE_DIR, "browser", "dashboard.html")
            self.browser.setUrl(QUrl.fromLocalFile(dashboard_path))
            return
        
        if not url.startswith("http"):
            url = f"https://www.google.com/search?q={url}"
        
        self.browser.setUrl(QUrl(url))
        self.save_last_url(url)


        # Function to create toolbar buttons
    def create_button(self, icon, tooltip, callback):
        btn = QToolButton()
        btn.setText(icon)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        return btn
        # Function to toggle full-screen mode
    def resize_browser(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()



    def change_theme(self):
        # Dynamically get all themes from the dropdown
        themes = [self.theme_selector.itemText(i) for i in range(self.theme_selector.count())]
        index = themes.index(self.current_theme)
        
        # Cycle through themes without crashing
        self.current_theme = themes[(index + 1) % len(themes)]
        self.apply_theme(self.current_theme)
        self.save_config("theme", self.current_theme)


    def apply_theme(self, theme):
        dashboard_path = os.path.join(Config.BASE_DIR, "browser", "dashboard.html")
        with open(dashboard_path, "r") as file:
            content = file.read()

        # Dynamically replace any existing theme with the new one
        for t in [self.theme_selector.itemText(i) for i in range(self.theme_selector.count())]:
            content = content.replace(f'class="{t}"', f'class="{theme}"')

        with open(dashboard_path, "w") as file:
            file.write(content)

        #  Inject the theme without page reset
        self.inject_css_theme(theme)

        # Force the theme to stay even after page reloads
        script = """
            localStorage.setItem('catia_theme', '{}');
            window.addEventListener('DOMContentLoaded', () => {{
                let theme = localStorage.getItem('catia_theme');
                document.body.className = theme;
            }});
        """.format(theme)
        self.browser.page().runJavaScript(script)


    def load_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            return

        # Load theme & wallpaper from the config
        with open(self.CONFIG_FILE, "r") as file:
            data = json.load(file)

        self.current_theme = data.get("theme", "dark")
        self.current_wallpaper = data.get("wallpaper", "file:///default.jpg")

    def save_config(self, key, value):
    # Only convert to "file:///" if it's not already a URL
        if key == "wallpaper" and not value.startswith("file:///"):
            value = pathlib.Path(value).as_uri()

        if not os.path.exists(self.CONFIG_FILE):
            data = {}
        else:
            with open(self.CONFIG_FILE, "r") as file:
                data = json.load(file)

        data[key] = value

        with open(self.CONFIG_FILE, "w") as file:
            json.dump(data, file, indent=4)

    #Function to load browsing history
    def load_history(self):
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w") as file:
                file.write("")
        with open(self.HISTORY_FILE, "r") as file:
            history_data = file.readlines()

        self.history_list.clear()
        for entry in history_data:
            item = QListWidgetItem(entry.strip())
            self.history_list.addItem(item)

    # Clear history
    def clear_history(self):
        with open(self.HISTORY_FILE, "w") as file:
            file.write("")
        self.history_list.clear()

    # Clear bookmarks
    def clear_bookmarks(self):
        with open(self.BOOKMARKS_FILE, "w") as file:
            json.dump({}, file)
        self.bookmarks_list.clear()

    # Open downloads folder
    def open_downloads(self):
        os.startfile(Config.DOWNLOADS_DIR)

    #  Return to home/dashboard
    def go_home(self):
        dashboard_path = os.path.join(Config.BASE_DIR, "browser", "dashboard.html")
        self.browser.setUrl(QUrl.fromLocalFile(dashboard_path))

    def load_last_url(self):
        if not os.path.exists(self.CONFIG_FILE):
            return
        
        #  Load the last URL from config
        with open(self.CONFIG_FILE, "r") as file:
            data = json.load(file)
        
        last_url = data.get("last_url", "")
        if last_url:
            self.browser.setUrl(QUrl(last_url))

    def save_last_url(self, url):
        # ✅ Update config with the last opened URL
        if not os.path.exists(self.CONFIG_FILE):
            data = {}
        else:
            with open(self.CONFIG_FILE, "r") as file:
                data = json.load(file)
        
        data["last_url"] = url
        with open(self.CONFIG_FILE, "w") as file:
            json.dump(data, file, indent=4)


    # Stop loading the current page
    def stop_loading(self):
        self.browser.stop()

    def inject_css_theme(self, theme):
        # Pre-built CSS for different themes
        themes_css = {
            "dark": """
                * { background-color: #121212 !important; color: #e0e0e0 !important; }
                a { color: #bb86fc !important; }
            """,
            "light": """
                * { background-color: #ffffff !important; color: #000000 !important; }
            """,
            "cyberpunk": """
                * { background-color: #0a0a0a !important; color: #0ff !important; font-family: 'Orbitron', sans-serif; }
                a { color: #f80 !important; }
            """,
            "blade_runner": """
                * { background-color: #1a1a1a !important; color: #f0f0f0 !important; }
                a { color: #ff5555 !important; }
            """,
            "neon": """
                * { background-color: #000000 !important; color: #39ff14 !important; }
                a { color: #ff00ff !important; }
            """,
            "edgerunners": """
                * { background-color: #101010 !important; color: #ffcc00 !important; font-family: 'Bebas Neue', cursive; }
                a { color: #ff0099 !important; }
            """,
            "gothic": """
                * { background-color: #0f0f0f !important; color: #c0c0c0 !important; font-family: 'Cinzel', serif; }
                a { color: #8a2be2 !important; }
            """
        }

        #  Inject CSS into all web pages without resetting
        selected_css = themes_css.get(theme, themes_css["dark"])
        script = f"""
            var css = `{selected_css}`;
            var style = document.createElement('style');
            style.innerHTML = css;
            document.head.appendChild(style);
        """
        self.browser.page().runJavaScript(script)

