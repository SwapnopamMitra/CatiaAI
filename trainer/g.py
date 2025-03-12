import json
import re

def is_gibberish(text):
    """Checks if text is likely gibberish or repetitive nonsense."""
    if not text:
        return True
    if len(text.split()) < 3:  # Too short
        return True
    if re.search(r'\d{4,}', text):  # Random long numbers
        return True
    gibberish_patterns = [
        r"[^\w\s]{3,}",  # Too many special characters
        r"[A-Za-z]+\d+[A-Za-z]+",  # Mixed letters and numbers
        r"(?:\b\w+\b)(?:\s+\b\w+\b)+",  # Repeated words (fixed)
        r"Talk dirty to me.*Talk dirty to me",  # Duplicated inputs
        r"Ugh, do I have to\?",  # Low-effort responses (escaped `?`)
        r"You will listen and obey",  # Broken AI-generated responses
        r".*tumblr.*",  # Irrelevant Tumblr references (fixed)
        r".*Yuzu You'll get the idea.*",  # Meaningless text
        r".*Posted : \d+/\d+.*"  # Dates from AI generations
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in gibberish_patterns)

def clean_training_data(file_path, output_file):
    """Cleans training data by removing duplicates and gibberish."""
    cleaned_data = []
    removed_data = []
    seen_inputs = set()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            input_text = item.get("input", "").strip()
            output_text = item.get("output", "").strip()

            if not input_text or not output_text:
                removed_data.append(item)
                continue
            if input_text in seen_inputs:
                removed_data.append(item)
                continue
            if is_gibberish(output_text):
                removed_data.append(item)
                continue

            seen_inputs.add(input_text)
            cleaned_data.append({"input": input_text, "output": output_text})

    if removed_data:
        with open("removed_entries.json", "w", encoding="utf-8") as f:
            json.dump(removed_data, f, indent=4, ensure_ascii=False)
        print(f"⚠ Removed {len(removed_data)} bad entries. Check 'removed_entries.json' for details.")

    if not cleaned_data:
        raise ValueError("🚨 No valid training data found! All entries were removed.")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Cleaned training data saved to: {output_file}")

# Run the cleaning script
file_path = "C:/Users/swapn/OneDrive/Desktop/Prog/SideProjects/Catia/trainer/training_data.json"
output_file = "C:/Users/swapn/OneDrive/Desktop/Prog/SideProjects/Catia/trainer/cleaned_training_data.json"

clean_training_data(file_path, output_file)
