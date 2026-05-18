

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=API_KEY)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Hi my name is Mahitha. I am doing an LLM call for the first time, Its so exciting. Write a short bio about me.',
)
print(response.text)