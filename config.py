import os

class Config:
    # General settings
    APP_NAME = "Catia"
    VERSION = "1.0"

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BOOT_VIDEO = os.path.join(BASE_DIR, "boot", "catia.mp4")
    IDLE_VIDEO = os.path.join(BASE_DIR, "boot", "catia_idle.mp4")
    MEMORY_FILE = os.path.join(BASE_DIR, "memory", "catia_memory.enc")
    MEMORY_KEY = os.path.join(BASE_DIR, "memory", "memory_key.key")

    # Voice settings
    VOICE_RATE = 170
    VOICE_VOLUME = 1.0
    VOICE_GENDER = 1  # 0 = Male, 1 = Female

    # GUI settings
    DEFAULT_WINDOW_WIDTH = 1024
    DEFAULT_WINDOW_HEIGHT = 600
    FULLSCREEN = False

    # Browser settings
    HOMEPAGE = "https://search.brave.com/"

