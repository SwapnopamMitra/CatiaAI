from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class CatiaLLM:
    def __init__(self):
        self.model = AutoModelForCausalLM.from_pretrained("./trained_catia")
        self.tokenizer = AutoTokenizer.from_pretrained("./trained_catia")

    def think(self, user_input):
        inputs = self.tokenizer(user_input, return_tensors="pt", padding=True)
        outputs = self.model.generate(**inputs, max_length=100)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# ✅ Example usage
catia = CatiaLLM()
response = catia.think("hey")
print("Catia:", response)
