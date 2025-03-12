import os
import time

while True:
    print("🔥 Generating new NSFW training data...")
    os.system("python nsfw_generator.py")  # Runs the chatbot generator

    print("📚 Updating and training model...")
    os.system("python train.py")  # Runs training with the updated dataset

    print("✅ Model updated! Sleeping for 24 hours...")
    time.sleep(86400)  # Runs once a day
import os
import time

while True:
    print("🔥 Generating new NSFW training data...")
    os.system("python nsfw_generator.py")  # Runs the chatbot generator

    print("📚 Updating and training model...")
    os.system("python train.py")  # Runs training with the updated dataset

    print("✅ Model updated! Sleeping for 24 hours...")
    time.sleep(86400)  # Runs once a day
