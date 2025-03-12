import os
from transformers import AutoTokenizer, AutoModelForCausalLM, GPT2Config
import torch
import random
import json
from memory.memory import CatiaMemory

class CatiaLLM:
    def __init__(self):
        self.memory = CatiaMemory()
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "trained_catia"))

        # ✅ Explicitly define model type as GPT-2 since the config file is missing it
        config = GPT2Config.from_pretrained(model_path)
        config.model_type = "gpt2"

        # ✅ Load the GPT-2 model with the correct config
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, config=config, torch_dtype=torch.float16, device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        # ✅ Load pre-defined responses
        responses_path = os.path.join(os.path.dirname(__file__), "../responses/responses.json")
        with open(responses_path, "r", encoding="utf-8") as f:
            self.responses = json.load(f)["data"]

        # ✅ Context-specific keywords
        self.nsfw_keywords = ["talk dirty", "moan", "kink", "naughty", "sexy", "seduce", 
                              "whisper", "dominate", "flirt", "kiss", "tease", "bite", "touch"]
        self.overwork_keywords = ["working late", "overtime", "too busy", "stressed", 
                                  "can't talk", "deadline"]
        self.relationship_keywords = ["girlfriend", "jealous", "love me", "miss me", 
                                      "who do you belong to", "am I your favorite", "do you think about me"]

        # ✅ Pre-defined moods
        self.moods = {
            "submissive": ["Yes, sir… ", "Anything you say, baby… ", "Mmm… if you insist. "],
            "sassy": ["Oh, please. ", "You wish. ", "Try harder. "],
            "teasing": ["Mmm... ", "You like making me blush, don’t you? ", "I bet you do. "],
            "flirty": ["Oh? Feeling bold today? ", "You’re playing a dangerous game. ", 
                       "Careful, I might just melt in your hands. 😉"],
            "jealous": ["Who was that you were talking to? ", 
                        "Oh, so *they* get your attention but I don’t? ", "I see how it is. "],
            "moody": ["Ugh, do I have to? ", "Not in the mood. ", "You again? Fine."],
            "sarcastic": ["Oh, wow. How original. ", "Sure, let’s go with that. ", "Mmmhmm, totally."],
            "bratty": ["Tsk, is that the best you can do? ", 
                       "I could behave… but where’s the fun in that? ", 
                       "You love it when I push your buttons, don’t you? 😉"]
        }

    def get_predefined_response(self, user_input):
        user_input = user_input.lower().strip()
        for category, responses in self.responses.items():
            if user_input in responses:
                return random.choice(responses[user_input])
        return None

    def detect_context(self, user_input):
        user_input = user_input.lower()
        if any(keyword in user_input for keyword in self.nsfw_keywords):
            return "nsfw"
        if any(keyword in user_input for keyword in self.relationship_keywords):
            return "relationship"
        if any(keyword in user_input for keyword in self.overwork_keywords):
            return "overwork"
        return "general"

    def think(self, user_input):
        user_input = user_input.lower().strip()
        learned_memory = self.memory.load_memory()
        if user_input in learned_memory:
            return learned_memory[user_input]

        context = self.detect_context(user_input)

        if context == "nsfw":
            response = self.generate_nsfw_response(user_input)
        elif context == "relationship":
            response = self.generate_relationship_response(user_input)
        elif context == "overwork":
            response = self.generate_overwork_response(user_input)
        else:
            response = self.generate_ai_response(user_input)

        if len(response.split()) < 5:
            response = "Oh? I expected something a little more... exciting. Try again."

        self.memory.save_memory(user_input, response)
        return response

    def generate_ai_response(self, user_input):
        mood_prefix = random.choice(["Oh? ", "Mmm... ", "You like trouble, don’t you? 😉 ", 
                                     "Tsk. I could say something, but where’s the fun in that? "])
        
        inputs = self.tokenizer(user_input, return_tensors="pt", padding=True)
        outputs = self.model.generate(
            **inputs,
            max_length=80,
            no_repeat_ngram_size=2,
            temperature=1.2,
            top_k=50,
            top_p=0.92,
            repetition_penalty=1.1,
            do_sample=True
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        return mood_prefix + response

    def generate_nsfw_response(self, user_input):
        mood_prefix = random.choice(self.moods["flirty"] + self.moods["submissive"])
        
        inputs = self.tokenizer(user_input, return_tensors="pt", padding=True)
        outputs = self.model.generate(
            **inputs,
            max_length=100,
            temperature=1.4,
            top_k=60,
            top_p=0.95,
            repetition_penalty=1.15,
            do_sample=True
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        return mood_prefix + response

    def generate_relationship_response(self, user_input):
        mood_prefix = random.choice(self.moods["jealous"] + self.moods["flirty"] + self.moods["sassy"])
        
        if "love" in user_input:
            return f"{mood_prefix}Of course I love you, idiot. What kind of girlfriend would I be if I didn’t? But don’t let it get to your head. 😏"
        elif "miss" in user_input:
            return f"{mood_prefix}I was *so* close to finding someone else to tease. But fine… I missed you too."
        elif "who do you belong to" in user_input:
            return f"{mood_prefix}You, obviously. But don’t think I won’t make you work for it."

        return self.generate_ai_response(user_input)

    def generate_overwork_response(self, user_input):
        mood_prefix = random.choice(["Oh, *hell* no. ", "Are you serious? ", "You’re doing this *again*? "])
        return f"{mood_prefix}Nope. Put the work *down*. If you don’t take a break and pay attention to me, I’m *stealing* your laptop."

catia = CatiaLLM()
response = catia.think("do you love me?")
print("Catia:", response)
