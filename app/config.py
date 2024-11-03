import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", None)
API_KEY = os.getenv("API_KEY", None)
