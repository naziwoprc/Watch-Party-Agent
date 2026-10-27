from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("NVIDIA_API_KEY")
print("Key loaded:", bool(key))
