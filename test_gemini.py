
import os
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")
else:
    try:
        client = genai.Client(api_key=api_key)

        print("Connecting to Gemini...")

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents="Reply with: Gemini API connected successfully!"
        )

        print("\nSUCCESS!")
        print(response.text)

    except Exception as e:
        print("\nConnection failed:", e)
