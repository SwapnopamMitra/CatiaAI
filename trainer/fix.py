import json

def fix_json(file_path):
    """Fixes a broken JSON file by adding missing commas and validating the structure."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ✅ Step 1: Ensure the content is properly enclosed in a list
    if not content.strip().startswith("["):
        print("⚠ ERROR: The JSON file must start with '[' (list of objects).")
        return
    
    # ✅ Step 2: Fix missing commas by ensuring each object is separated correctly
    content = content.strip()

    # 1. Ensure it starts and ends with square brackets
    if not content.startswith("["):
        content = "[" + content
    if not content.endswith("]"):
        content = content + "]"

    # 2. Fix missing commas between objects
    content = content.replace("}\n{", "},\n{")  # Fix missing commas
    content = content.replace("}{", "},{")  # Edge cases

    # ✅ Step 3: Try parsing the fixed JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON is still invalid after fixing! Error: {e}")
        return

    # ✅ Step 4: Save the corrected JSON
    fixed_file_path = file_path.replace(".json", "_fixed.json")
    with open(fixed_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ JSON file fixed and saved as: {fixed_file_path}")

# 🔥 Run the script (modify with your actual file path)
fix_json("training_data.json")
