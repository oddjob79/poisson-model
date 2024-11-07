import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_URL = os.getenv("API_URL", None)
    API_KEY = os.getenv("API_KEY", None)

    DB_USER = os.getenv("POSTGRES_USER", None)
    DB_PASS = os.getenv("POSTGRES_PASS", None)
    DB_HOST = os.getenv("POSTGRES_HOST", None)
    DB_CREDS = f"{DB_USER}:{DB_PASS}@{DB_HOST}"
    DB_PORT = 5432
    DB_NAME = "poisson"

    DB_CONN_STR = f"postgresql+psycopg://{DB_CREDS}:{DB_PORT}/{DB_NAME}"