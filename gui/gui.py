from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLineEdit
from PyQt5.QtCore import Qt
from boot.boot import BootScreen  

from config import Config
from assistant.assistant import CatiaAssistant
from browser.browser import CatiaBrowser
#from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLineEdit
from PyQt5.QtWidgets import QHBoxLayout



class CatiaGUI(QMainWindow):
    def __init__(self, assistant):  # ✅ Accept assistant as a parameter
        super().__init__()
        self.setWindowTitle(Config.APP_NAME)
        self.setGeometry(100, 100, Config.DEFAULT_WINDOW_WIDTH, Config.DEFAULT_WINDOW_HEIGHT)
        self.fullscreen = Config.FULLSCREEN

        # ✅ Fix: Store the passed assistant instance
        self.assistant = assistant  

        # Chat Box
        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)

        # ✅ Show greeting in the chat box after assistant is initialized
        initial_greeting = self.assistant.format_response(self.assistant.get_greeting())
        self.chat_box.append(f"Catia: {initial_greeting}\n")

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Type something and press Enter...")
        self.user_input.returnPressed.connect(self.process_input)

        # ✅ Define layout before adding widgets
        layout = QVBoxLayout()


        # Buttons
        self.listen_button = QPushButton("🎤 Listen", self)
        self.listen_button.clicked.connect(self.listen_to_user)
        layout.addWidget(self.listen_button)

        self.browser_button = QPushButton("Open Browser", self)
        self.browser_button.clicked.connect(self.open_browser)
        layout.addWidget(self.browser_button)

        self.toggle_button = QPushButton("Toggle Fullscreen", self)
        self.toggle_button.clicked.connect(self.toggle_fullscreen)
        layout.addWidget(self.toggle_button)

        layout.addWidget(self.chat_box)
        layout.addWidget(self.user_input)

        # ✅ Toolbar layout (correctly integrated now)
        toolbar_layout = QHBoxLayout()
        self.manage_memory_button = QPushButton("Manage Memory")
        self.manage_memory_button.clicked.connect(self.manage_memory)
        toolbar_layout.addWidget(self.manage_memory_button)

        # ✅ Combine layouts properly
        layout.addLayout(toolbar_layout)

        # ✅ Set layout once
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def process_input(self):
        text = self.user_input.text()
        if text.strip():
            response = self.assistant.respond(text)
            self.chat_box.append(f"You: {text}\nCatia: {response}\n")
            self.user_input.clear()

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.fullscreen = not self.fullscreen

    def open_browser(self):
        self.browser = CatiaBrowser()
        self.browser.show()

    def listen_to_user(self):
        self.chat_box.append("Listening...")
        user_input = self.assistant.voice.listen()
        self.chat_box.append(f"You (via voice): {user_input}")
        response = self.assistant.respond(user_input)
        self.chat_box.append(f"Catia: {response}\n")
    def manage_memory(self):
        memory_data = self.assistant.memory.load_memory()
        
        # Create a window to list all memory
        self.memory_window = QWidget()
        layout = QVBoxLayout()
        
        for key, value in memory_data.items():
            btn = QPushButton(f"{key} → {value}")
            btn.clicked.connect(lambda _, k=key: self.delete_memory(k))
            layout.addWidget(btn)
        
        self.memory_window.setLayout(layout)
        self.memory_window.setWindowTitle("Memory Manager")
        self.memory_window.show()

    def delete_memory(self, key):
        self.assistant.memory.delete_memory(key)
        self.memory_window.close()
        self.manage_memory()  # Refresh the memory window

