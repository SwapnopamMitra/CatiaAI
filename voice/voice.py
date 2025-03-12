import pyttsx3
import speech_recognition as sr
from config import Config

class CatiaVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", Config.VOICE_RATE)
        self.engine.setProperty("volume", Config.VOICE_VOLUME)

        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[Config.VOICE_GENDER].id)

        self.recognizer = sr.Recognizer()

    def speak(self, text):
        """Speaks out text while preventing the 'run loop already started' error."""
        try:
            self.engine.stop()  # ✅ Stops any previous speech to avoid crashes
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            print("⚠ Voice engine already running. Skipping speech to prevent crash.")

    def listen(self):
        """Listens to the microphone and processes voice input safely."""
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)  # ✅ Adapts to background noise
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                return self.recognizer.recognize_google(audio).lower()
            except sr.WaitTimeoutError:
                return "I didn't hear anything. Try again."
            except sr.UnknownValueError:
                return "I didn't catch that."
            except sr.RequestError:
                return "Speech recognition service is unavailable."
