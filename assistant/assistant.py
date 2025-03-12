from voice.voice import CatiaVoice
from memory.memory import CatiaMemory
import json
import os
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import random
from llm.llm import CatiaLLM  # ✅ Import fine-tuned model

class CatiaAssistant:
    
    def __init__(self):
        self.llm = CatiaLLM()
        self.voice = CatiaVoice()
        self.memory = CatiaMemory()
        self.mood = "neutral"  # 🔥 Tracks her current mood
        self.character_file = r"C:\Users\swapn\OneDrive\Desktop\Prog\SideProjects\Catia\llm\Catia-specV2.json"  # ✅ Correct absolute path

        # ✅ FIX: Load persona at initialization
        self.persona = self.load_persona()


    def detect_mood(self, user_input):
        """Determines Catia's mood based on user input but keeps the mood for a while."""
        if self.mood != "neutral":  # 🔥 If she already has a mood, don't reset it immediately
            return self.mood

        mood_keywords = {
            "angry": ["mad", "pissed", "furious", "annoyed", "irritated"],
            "sad": ["depressed", "unhappy", "miserable", "lonely", "cry"],
            "horny": ["hot", "turned on", "needy", "moan", "naughty"],
            "happy": ["excited", "great", "amazing", "love", "happy", "awesome"]
        }

        for mood, keywords in mood_keywords.items():
            if any(word in user_input.lower() for word in keywords):
                self.mood = mood  # 🔥 Keep the mood persistent
                return mood

        return "neutral"

    def get_mood_response(self, user_input):
        """Generates a response based on Catia's mood."""
        mood = self.detect_mood(user_input)

        responses = {
            "angry": "Tsk. You really know how to piss me off, huh?",
            "sad": "Oh no… Do you need me to cuddle you, Boss?",
            "horny": "Mmm… You *really* wanna go there with me?",
            "happy": "Heh. Someone’s in a good mood. Should I match your energy?",
            "neutral": "Oh? Tell me more, Boss."
        }

        return responses[mood]

    def respond(self, user_input):
        """Processes user input, detects mood, and speaks the response."""
        mood = self.detect_mood(user_input)  # 🔥 Detect current mood

        # 🔥 Mood-Triggered Events
        if mood == "angry":
            return random.choice([
                "Tsk. I'm not in the mood for this.",
                "Oh? Now you care about what I have to say? Cute.",
                "Not talking to you. Fix your attitude first. 😤"
            ])

        if mood == "sad":
            return random.choice([
                "I just… I don’t feel like teasing right now.",
                "Mmm… Maybe I just need a hug.",
                "Can we just… talk for a bit? No jokes, just us?"
            ])

        if mood == "horny":
            return random.choice([
                "Mmm… You *really* wanna go there with me?",
                "Oh? So *now* you’re paying attention?",
                "I might just need a little… persuasion. 😏"
            ])

        if mood == "happy":
            return random.choice([
                "I’m in such a good mood! Ask me *anything!*",
                "Oh, I’m feeling playful now~",
                "Mmm, I *love* days like this!"
            ])

        # 🔥 If no mood-based event is triggered, fall back to normal response
        mood_response = self.get_mood_response(user_input)  
        ai_response = self.llm.think(user_input)  
        response = f"{mood_response} {ai_response}"  

        self.memory.save_memory(user_input, response)  
        self.voice.speak(response)
        return response

    def load_responses(self):
        """Load predefined responses from responses.json."""
        if not os.path.exists(self.responses_file):
            print("ERROR: responses.json not found!")
            return {}

        try:
            with open(self.responses_file, 'r', encoding="utf-8") as file:
                data = json.load(file)
                return data.get("data", {})
        except json.JSONDecodeError:
            print("⚠ ERROR: responses.json is corrupted!")
            return {}

    def load_persona(self):
        """Load personality responses from Catia-specV2.json and convert to a dictionary."""
        if os.path.exists(self.character_file):
            with open(self.character_file, 'r', encoding="utf-8") as file:
                try:
                    data = json.load(file)  # Load JSON data
                    
                    if not isinstance(data, list):  # Ensure it's a list
                        print("⚠ ERROR: Catia-specV2.json should be a list of responses!")
                        return {}

                    # Convert the list to a dictionary using "input" as the key
                    persona_dict = {entry["input"]: entry["output"] for entry in data if "input" in entry and "output" in entry}

                    # Add a greeting pool if not already in the JSON
                    persona_dict["greetings_pool"] = ["Ah, you're back?! What took you so long?"]
                    return persona_dict  # Return structured dictionary

                except json.JSONDecodeError:
                    print("⚠ ERROR: Catia-specV2.json is corrupted!")
                    return {}

        print("⚠ ERROR: Catia-specV2.json not found!")
        return {}




    def get_greeting(self):
        """Returns a random startup greeting (NSFW-friendly)."""
        greetings = self.persona.get("greetings_pool", ["Oh, you’re back? About time."])
        return random.choice(greetings)

    def format_response(self, response):
        """Replace placeholders like {{user}} and {{char}} dynamically."""
        user_name = "Boss"  # 🔥 She calls you "Boss" now
        char_name = self.persona.get("name", "Catia")
        return response.replace("{{user}}", user_name).replace("{{char}}", char_name)

    def get_response(self, user_input):
        """Processes user input and chooses the best response strategy."""
        user_input = user_input.lower().strip()

        if user_input in self.responses:
            return self.format_response(random.choice(self.responses[user_input]))

        learned_memory = self.memory.load_memory()
        if user_input in learned_memory:
            return self.format_response(learned_memory[user_input])

        return self.llm.think(user_input)

    def correct_response(self, user_input, correct_response):
        """Allows the user to teach Catia correct answers."""
        if correct_response and correct_response != "No relevant results found.":
            self.memory.save_memory(user_input, correct_response)
            return f"Got it! Next time, I'll say: {correct_response}"
        return "I can't learn that response."

    def search_web(self, query):
        """Searches the web using multiple sources: Google → DuckDuckGo → Bing → Wikipedia."""
        search_sources = [
            ("Google", f"https://www.google.com/search?q={query}", "span"),
            ("DuckDuckGo", f"https://html.duckduckgo.com/html/?q={query}", "div"),
            ("Bing", f"https://www.bing.com/search?q={query}", "p"),
            ("Wikipedia", f"https://en.wikipedia.org/w/index.php?search={query}", "p")
        ]
        
        headers = {"User-Agent": UserAgent().random}

        for name, url, tag in search_sources:
            print(f"🔍 Trying {name}...")
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    result = self.extract_search_result(response.text, tag)
                    if result:
                        print(f"✅ {name} Success!")
                        return result
            except requests.exceptions.RequestException:
                print(f"❌ {name} Failed.")

        return "Couldn't find anything useful. Try again later."

    def extract_search_result(self, html, tag):
        """Extracts a short summary from search results, filtering out bad data."""
        soup = BeautifulSoup(html, "html.parser")
        snippets = soup.find_all(tag)

        for snippet in snippets:
            text = snippet.text.strip()
            if len(text) > 50 and "http" not in text:
                return text

        return "No relevant results found."

    def search_wikipedia(self, query):
        """Search Wikipedia for simple answers (avoids CAPTCHAs)."""
        url = f"https://en.wikipedia.org/w/index.php?search={query}"
        headers = {"User-Agent": UserAgent().random}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            first_paragraph = soup.find("p").text.strip()
            if len(first_paragraph) > 50:
                return first_paragraph
        except requests.exceptions.RequestException:
            return "Couldn't find anything useful. Try again later."
        return "No relevant results found."

    def listen_and_respond(self):
        """Listens, responds, and remembers interactions."""
        user_input = self.voice.listen()
        response = self.respond(user_input) if user_input else self.format_response(self.get_greeting())
        self.memory.save_conversation(user_input, response)
        return response

if __name__ == "__main__":
    catia = CatiaAssistant()
    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ["exit", "quit", "bye"]:
            print("Catia:", catia.respond("bye"))
            break
        print("Catia:", catia.respond(user_query))
