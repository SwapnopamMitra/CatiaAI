import json
from cryptography.fernet import Fernet
import os
from difflib import get_close_matches



class CatiaMemory:
    def __init__(self):
        self.filepath = "memory/catia_memory.enc"
        self.keypath = "memory/memory_key.key"

        # ✅ Generate or Load Encryption Key
        if not os.path.exists(self.keypath):
            self.key = Fernet.generate_key()
            with open(self.keypath, "wb") as key_file:
                key_file.write(self.key)
        else:
            with open(self.keypath, "rb") as key_file:
                self.key = key_file.read()

        self.fernet = Fernet(self.key)

        # ✅ Ensure memory file exists
        if not os.path.exists(self.filepath):
            with open(self.filepath, "wb") as file:
                file.write(self.fernet.encrypt(json.dumps({}).encode()))

    def save_memory(self, key, value):
        """Encrypts and stores memory data while preventing overwriting similar inputs and keeping categories."""
        memory = self.load_memory()

        # ✅ Ensure memory categories exist
        categories = ["flirtation", "jokes", "casual", "facts", "questions", "greetings", "goodbyes", "affirmations", "negations"]
        for category in categories:
            if category not in memory:
                memory[category] = {}

        # ✅ Detect category based on user input
        flirt_keywords = ["beautiful", "hot", "gorgeous", "sexy", "cute", "stunning", "ravishing", "luscious"]
        joke_keywords = ["joke", "funny", "laugh"]
        fact_keywords = ["what is", "who is", "tell me about", "explain", "define"]
        question_keywords = ["how", "why", "when", "where", "does", "can", "is", "should", "will"]
        greeting_keywords = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "yo", "sup"]
        goodbye_keywords = ["bye", "goodbye", "see you", "later", "farewell", "take care"]
        affirmation_keywords = ["yes", "yeah", "yep", "sure", "absolutely", "of course"]
        negation_keywords = ["no", "nah", "nope", "never", "not really"]

        key_lower = key.lower()

        if any(word in key_lower for word in flirt_keywords):
            category = "flirtation"
        elif any(word in key_lower for word in joke_keywords):
            category = "jokes"
        elif any(word in key_lower for word in fact_keywords):
            category = "facts"
        elif any(word in key_lower for word in question_keywords):
            category = "questions"
        elif any(word in key_lower for word in greeting_keywords):
            category = "greetings"
        elif any(word in key_lower for word in goodbye_keywords):
            category = "goodbyes"
        elif any(word in key_lower for word in affirmation_keywords):
            category = "affirmations"
        elif any(word in key_lower for word in negation_keywords):
            category = "negations"
        else:
            category = "casual"  # Default category

        # ✅ Prevent saving bad responses
        bad_responses = [
            "Oh? You’ve been thinking about me? How scandalous!",
            "Wow, I'm blushing! If I had a face, that is.",
            "Flattery detected. Should I act impressed?",
            "No relevant results found.",
            "None",
            "DictionaryDefinitions from Oxford Languages"
        ]

        if not value or value.strip() in bad_responses:
            print(f"❌ Skipping memory save for: {key} → Invalid response")
            return

        # ✅ Check for similar responses before saving
        existing_responses = self.load_memory_fuzzy(key)

        if existing_responses:
            print(f"🔄 Updating existing memory for similar input: {key}")
        else:
            print(f"💾 Learning new {category} response: {key} → {value}")

        memory[category][key] = value

        with open(self.filepath, "wb") as file:
            file.write(self.fernet.encrypt(json.dumps(memory).encode()))

    def load_memory_fuzzy(self, user_input):
        """Finds memory responses for similar inputs, searching in all categories."""
        memory = self.load_memory()
        all_keys = []

        # Collect all stored user inputs across categories
        for category in memory.values():
            if isinstance(category, dict):
                all_keys.extend(category.keys())

        # Find closest 3 matches
        matches = get_close_matches(user_input, all_keys, n=3, cutoff=0.7)

        if matches:
            return [memory[category][match] for match in matches for category in memory if match in memory.get(category, {})]

        return None



    def load_memory(self, user_input=None):
        """Loads and decrypts memory data, with optional fuzzy matching."""
        try:
            with open(self.filepath, "rb") as file:
                encrypted_data = file.read()
                memory = json.loads(self.fernet.decrypt(encrypted_data).decode())

                # If a user input is provided, try fuzzy recall
                if user_input:
                    fuzzy_responses = self.load_memory_fuzzy(user_input)
                    if fuzzy_responses:
                        return {"fuzzy_matches": fuzzy_responses}  # ✅ Store inside a dictionary

                return memory
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def delete_memory(self, key):
        """Deletes a specific memory entry."""
        memory = self.load_memory()
        if key in memory:
            del memory[key]
            with open(self.filepath, "wb") as file:
                file.write(self.fernet.encrypt(json.dumps(memory).encode()))

    def clear_memory(self):
        """Completely clears stored memory."""
        with open(self.filepath, "wb") as file:
            file.write(self.fernet.encrypt(json.dumps({}).encode()))

    def save_conversation(self, user_input, response):
        """Stores full conversation history securely."""
        history = self.load_conversation()
        history.append({"user": user_input, "catia": response})
        with open("memory/conversation_log.json", "w") as file:
            file.write(json.dumps(history, indent=4))

    def load_conversation(self):
        """Loads past conversations."""
        try:
            with open("memory/conversation_log.json", "r") as file:
                return json.loads(file.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def store_interaction(self, user_input, catia_response):
        """Stores full interactions securely."""
        memory = self.load_memory()
        if "conversation_history" not in memory:
            memory["conversation_history"] = []
        memory["conversation_history"].append({"user": user_input, "catia": catia_response})

        # Keep memory manageable (only store last 20 interactions)
        memory["conversation_history"] = memory["conversation_history"][-20:]

        with open(self.filepath, "wb") as file:
            file.write(self.fernet.encrypt(json.dumps(memory).encode()))

    def save_feedback(self, user_input, correct_response):
        """Stores feedback and tracks repeated mistakes to improve learning."""
        memory = self.load_memory()
        
        if "incorrect_responses" not in memory:
            memory["incorrect_responses"] = {}

        # Track mistakes count
        if user_input in memory["incorrect_responses"]:
            memory["incorrect_responses"][user_input]["count"] += 1
        else:
            memory["incorrect_responses"][user_input] = {"response": correct_response, "count": 1}

        with open(self.filepath, "wb") as file:
            file.write(self.fernet.encrypt(json.dumps(memory).encode()))


    def get_feedback(self, user_input):
        """Retrieves corrected responses if available (fixes mistakes immediately)."""
        memory = self.load_memory()
        feedback_data = memory.get("incorrect_responses", {}).get(user_input)

        if feedback_data:  # Apply correction immediately instead of waiting for 3 mistakes
            return feedback_data["response"]
        
        return None  # Otherwise, Catia uses normal responses


    def save_emotion(self, emotion):
        """Stores the last 5 detected emotions securely."""
        memory = self.load_memory()
        
        if "_past_emotions" not in memory:
            memory["_past_emotions"] = []

        memory["_past_emotions"].append(emotion)

        # Keep only last 5 emotions to avoid overflow
        memory["_past_emotions"] = memory["_past_emotions"][-5:]

        with open(self.filepath, "wb") as file:
            file.write(self.fernet.encrypt(json.dumps(memory).encode()))


    def load_emotion(self):
        """Loads the most recent emotion and checks for trends."""
        memory = self.load_memory()
        
        emotions = memory.get("_past_emotions", ["neutral"])

        if len(emotions) >= 3 and all(e == emotions[-1] for e in emotions[-3:]):
            return f"{emotions[-1]} (strong trend detected)"  # Adds trend awareness
        
        return emotions[-1]  # Otherwise, return most recent emotion

    def save_recent_topic(self, user_input):
        """Tracks the last discussed topic to maintain context."""
        memory = self.load_memory()
        memory["_last_topic"] = user_input  # Store the last user query
        with open(self.filepath, "wb") as file:
            file.write(self.fernet.encrypt(json.dumps(memory).encode()))

    def get_recent_topic(self):
        """Retrieves the last discussed topic for context-aware responses."""
        memory = self.load_memory()
        return memory.get("_last_topic", None)


if __name__ == "__main__":
    catia_memory = CatiaMemory()
    catia_memory.save_memory("hello", "Hey there!")
    print("Stored Memory:", catia_memory.load_memory())
